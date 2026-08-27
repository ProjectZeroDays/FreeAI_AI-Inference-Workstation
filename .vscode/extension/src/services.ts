import * as vscode from "vscode";
import * as net from "net";
import * as http from "http";
import * as https from "https";
import * as path from "path";
import * as fs from "fs";
import { ServiceStatus, RouterResponse, RouterStreamEvent, DebugLog } from "./types";

export class ServiceManager {
  private services: ServiceStatus[] = [];
  private intervalId: NodeJS.Timeout | null = null;
  private workspaceRoot: string;
  private readonly config: vscode.WorkspaceConfiguration;
  private debugLogs: DebugLog[] = [];
  private mockMode: boolean = false;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.config = vscode.workspace.getConfiguration("freeai");
    this.workspaceRoot = this.detectWorkspaceRoot();
  }

  private detectWorkspaceRoot(): string {
    const configured = this.config.get<string>("workstationRoot", "");
    if (configured && fs.existsSync(configured)) {
      return configured;
    }
    const folders = vscode.workspace.workspaceFolders;
    if (folders) {
      for (const folder of folders) {
        const candidate = folder.uri.fsPath;
        if (fs.existsSync(path.join(candidate, "config", "services.json"))) {
          return candidate;
        }
      }
      return folders[0].uri.fsPath;
    }
    return "";
  }

  get servicesJsonPath(): string {
    return path.join(this.workspaceRoot, "config", "services.json");
  }

  get launchPyPath(): string {
    return path.join(this.workspaceRoot, "launch.py");
  }

  get checkHealthPyPath(): string {
    return path.join(this.workspaceRoot, "scripts", "check_health.py");
  }

  async loadServices(): Promise<ServiceStatus[]> {
    try {
      const raw = fs.readFileSync(this.servicesJsonPath, "utf8");
      const cfg = JSON.parse(raw);
      const entries = Object.entries(cfg.services || {});
      this.services = entries.map(([name, svc]: [string, any]) => ({
        name,
        port: svc.port,
        status: "down" as const,
        priority: svc.priority || "medium",
        healthPath: svc.health_path,
        dependencies: svc.dependencies || [],
        module: svc.module,
      }));
      await this.probeAll();
      return this.services;
    } catch {
      return [];
    }
  }

  async probeAll(): Promise<void> {
    const tasks = this.services.map((s) => this.probeService(s));
    await Promise.all(tasks);
  }

  private async probeService(svc: ServiceStatus): Promise<void> {
    const ok = await this.pingService(svc);
    svc.status = ok ? "ok" : "down";
  }

  private pingService(svc: ServiceStatus): Promise<boolean> {
    return new Promise((resolve) => {
      const start = Date.now();
      const sock = new net.Socket();
      sock.setTimeout(2000);
      sock.on("connect", () => {
        const elapsed = Date.now() - start;
        svc.latencyMs = elapsed;
        sock.destroy();
        if (svc.healthPath) {
          this.httpProbe(svc).then((httpOk) => {
            svc.status = httpOk ? "ok" : "degraded";
            resolve(httpOk);
          });
        } else {
          svc.status = "ok";
          resolve(true);
        }
      });
      sock.on("timeout", () => { sock.destroy(); resolve(false); });
      sock.on("error", () => resolve(false));
      sock.connect(svc.port, "127.0.0.1");
    });
  }

  private httpProbe(svc: ServiceStatus): Promise<boolean> {
    return new Promise((resolve) => {
      const url = `http://127.0.0.1:${svc.port}${svc.healthPath}`;
      const req = http.get(url, { timeout: 3000 }, (res) => {
        let data = "";
        res.on("data", (chunk) => { data += chunk; });
        res.on("end", () => {
          resolve(res.statusCode === 200);
        });
      });
      req.on("error", () => resolve(false));
      req.on("timeout", () => { req.destroy(); resolve(false); });
    });
  }

  startPolling(): void {
    if (this.intervalId) return;
    const ms = this.config.get<number>("refreshIntervalMs", 10000);
    this.intervalId = setInterval(async () => {
      await this.probeAll();
      this.emitStatusChange();
    }, ms);
  }

  stopPolling(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  onStatusChange(fn: (services: ServiceStatus[]) => void): vscode.Disposable {
    return this.statusChangeEmitter.event(fn);
  }
  private statusChangeEmitter = new vscode.EventEmitter<ServiceStatus[]>();

  emitStatusChange(): void {
    this.statusChangeEmitter.fire([...this.services]);
  }

  getServices(): ServiceStatus[] {
    return this.services;
  }

  getStatusDot(svc: ServiceStatus): string {
    switch (svc.status) {
      case "ok": return "$(check-all)";
      case "degraded": return "$(warning)";
      case "down": return "$(circle-slash)";
      default: return "$(circle-slash)";
    }
  }

  getStatusColor(svc: ServiceStatus): string {
    switch (svc.status) {
      case "ok": return "#26a64a";
      case "degraded": return "#e5a500";
      case "down": return "#f97583";
      default: return "#808080";
    }
  }

  async startServices(): Promise<boolean> {
    if (!this.workspaceRoot) {
      vscode.window.showErrorMessage("FreeAI: workstation root not found");
      return false;
    }
    this.addLog("system", "Starting services via launch.py...");
    try {
      const result = await vscode.commands.executeCommand(
        "workbench.action.terminal.open",
      );
      const { exec } = await import("child_process");
      return new Promise((resolve) => {
        exec(`python "${this.launchPyPath}"`, { cwd: this.workspaceRoot }, (err, stdout, stderr) => {
          if (err) {
            this.addLog("error", `Start failed: ${err.message}`);
            vscode.window.showErrorMessage(`FreeAI: Failed to start services — ${err.message}`);
            resolve(false);
          } else {
            this.addLog("system", `Started:\n${stdout}`);
            vscode.window.showInformationMessage("FreeAI: Services started");
            this.probeAll().then(() => this.emitStatusChange());
            resolve(true);
          }
        });
      });
    } catch (e) {
      this.addLog("error", `Start error: ${e}`);
      return false;
    }
  }

  async stopServices(): Promise<boolean> {
    if (!this.workspaceRoot) {
      vscode.window.showErrorMessage("FreeAI: workstation root not found");
      return false;
    }
    this.addLog("system", "Stopping services via launch.py...");
    try {
      const { exec } = await import("child_process");
      return new Promise((resolve) => {
        exec(`python "${this.launchPyPath}" --stop all`, { cwd: this.workspaceRoot }, (err, stdout, stderr) => {
          if (err) {
            this.addLog("error", `Stop failed: ${err.message}`);
            vscode.window.showErrorMessage(`FreeAI: Failed to stop services — ${err.message}`);
            resolve(false);
          } else {
            this.addLog("system", `Stopped:\n${stdout}`);
            vscode.window.showInformationMessage("FreeAI: Services stopped");
            this.services.forEach((s) => (s.status = "down"));
            this.emitStatusChange();
            resolve(true);
          }
        });
      });
    } catch (e) {
      this.addLog("error", `Stop error: ${e}`);
      return false;
    }
  }

  async startService(name: string): Promise<boolean> {
    if (!this.workspaceRoot) return false;
    this.addLog("system", `Starting ${name}...`);
    try {
      const { exec } = await import("child_process");
      return new Promise((resolve) => {
        exec(`python "${this.launchPyPath}" ${name}`, { cwd: this.workspaceRoot }, (err, stdout) => {
          if (err) {
            this.addLog("error", `Start ${name} failed: ${err.message}`);
            resolve(false);
          } else {
            this.addLog("system", `Started ${name}`);
            this.probeAll().then(() => this.emitStatusChange());
            resolve(true);
          }
        });
      });
    } catch {
      return false;
    }
  }

  async stopService(name: string): Promise<boolean> {
    if (!this.workspaceRoot) return false;
    this.addLog("system", `Stopping ${name}...`);
    try {
      const { exec } = await import("child_process");
      return new Promise((resolve) => {
        exec(`python "${this.launchPyPath}" --stop ${name}`, { cwd: this.workspaceRoot }, (err, stdout) => {
          if (err) {
            this.addLog("error", `Stop ${name} failed: ${err.message}`);
            resolve(false);
          } else {
            this.addLog("system", `Stopped ${name}`);
            const svc = this.services.find((s) => s.name === name);
            if (svc) { svc.status = "down"; this.emitStatusChange(); }
            resolve(true);
          }
        });
      });
    } catch {
      return false;
    }
  }

  getDebugLogs(): DebugLog[] {
    return [...this.debugLogs];
  }

  getLogs(): DebugLog[] {
    return this.debugLogs;
  }

  clearLogs(): void {
    this.debugLogs = [];
  }

  setMockMode(enabled: boolean): void {
    this.mockMode = enabled;
    this.addLog("system", `MOCK_LLM mode ${enabled ? "ENABLED" : "DISABLED"}`);
  }

  isMockMode(): boolean {
    return this.mockMode;
  }

  private addLog(type: DebugLog["type"], message: string, data?: unknown): void {
    this.debugLogs.push({ ts: new Date().toISOString(), type, message, data });
    if (this.debugLogs.length > 500) this.debugLogs.shift();
  }
}
