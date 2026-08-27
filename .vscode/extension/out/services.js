"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ServiceManager = void 0;
const vscode = __importStar(require("vscode"));
const net = __importStar(require("net"));
const http = __importStar(require("http"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
class ServiceManager {
    context;
    services = [];
    intervalId = null;
    workspaceRoot;
    config;
    debugLogs = [];
    mockMode = false;
    constructor(context) {
        this.context = context;
        this.config = vscode.workspace.getConfiguration("freeai");
        this.workspaceRoot = this.detectWorkspaceRoot();
    }
    detectWorkspaceRoot() {
        const configured = this.config.get("workstationRoot", "");
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
    get servicesJsonPath() {
        return path.join(this.workspaceRoot, "config", "services.json");
    }
    get launchPyPath() {
        return path.join(this.workspaceRoot, "launch.py");
    }
    get checkHealthPyPath() {
        return path.join(this.workspaceRoot, "scripts", "check_health.py");
    }
    async loadServices() {
        try {
            const raw = fs.readFileSync(this.servicesJsonPath, "utf8");
            const cfg = JSON.parse(raw);
            const entries = Object.entries(cfg.services || {});
            this.services = entries.map(([name, svc]) => ({
                name,
                port: svc.port,
                status: "down",
                priority: svc.priority || "medium",
                healthPath: svc.health_path,
                dependencies: svc.dependencies || [],
                module: svc.module,
            }));
            await this.probeAll();
            return this.services;
        }
        catch {
            return [];
        }
    }
    async probeAll() {
        const tasks = this.services.map((s) => this.probeService(s));
        await Promise.all(tasks);
    }
    async probeService(svc) {
        const ok = await this.pingService(svc);
        svc.status = ok ? "ok" : "down";
    }
    pingService(svc) {
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
                }
                else {
                    svc.status = "ok";
                    resolve(true);
                }
            });
            sock.on("timeout", () => { sock.destroy(); resolve(false); });
            sock.on("error", () => resolve(false));
            sock.connect(svc.port, "127.0.0.1");
        });
    }
    httpProbe(svc) {
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
    startPolling() {
        if (this.intervalId)
            return;
        const ms = this.config.get("refreshIntervalMs", 10000);
        this.intervalId = setInterval(async () => {
            await this.probeAll();
            this.emitStatusChange();
        }, ms);
    }
    stopPolling() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    onStatusChange(fn) {
        return this.statusChangeEmitter.event(fn);
    }
    statusChangeEmitter = new vscode.EventEmitter();
    emitStatusChange() {
        this.statusChangeEmitter.fire([...this.services]);
    }
    getServices() {
        return this.services;
    }
    getStatusDot(svc) {
        switch (svc.status) {
            case "ok": return "$(check-all)";
            case "degraded": return "$(warning)";
            case "down": return "$(circle-slash)";
            default: return "$(circle-slash)";
        }
    }
    getStatusColor(svc) {
        switch (svc.status) {
            case "ok": return "#26a64a";
            case "degraded": return "#e5a500";
            case "down": return "#f97583";
            default: return "#808080";
        }
    }
    async startServices() {
        if (!this.workspaceRoot) {
            vscode.window.showErrorMessage("FreeAI: workstation root not found");
            return false;
        }
        this.addLog("system", "Starting services via launch.py...");
        try {
            const result = await vscode.commands.executeCommand("workbench.action.terminal.open");
            const { exec } = await Promise.resolve().then(() => __importStar(require("child_process")));
            return new Promise((resolve) => {
                exec(`python "${this.launchPyPath}"`, { cwd: this.workspaceRoot }, (err, stdout, stderr) => {
                    if (err) {
                        this.addLog("error", `Start failed: ${err.message}`);
                        vscode.window.showErrorMessage(`FreeAI: Failed to start services — ${err.message}`);
                        resolve(false);
                    }
                    else {
                        this.addLog("system", `Started:\n${stdout}`);
                        vscode.window.showInformationMessage("FreeAI: Services started");
                        this.probeAll().then(() => this.emitStatusChange());
                        resolve(true);
                    }
                });
            });
        }
        catch (e) {
            this.addLog("error", `Start error: ${e}`);
            return false;
        }
    }
    async stopServices() {
        if (!this.workspaceRoot) {
            vscode.window.showErrorMessage("FreeAI: workstation root not found");
            return false;
        }
        this.addLog("system", "Stopping services via launch.py...");
        try {
            const { exec } = await Promise.resolve().then(() => __importStar(require("child_process")));
            return new Promise((resolve) => {
                exec(`python "${this.launchPyPath}" --stop all`, { cwd: this.workspaceRoot }, (err, stdout, stderr) => {
                    if (err) {
                        this.addLog("error", `Stop failed: ${err.message}`);
                        vscode.window.showErrorMessage(`FreeAI: Failed to stop services — ${err.message}`);
                        resolve(false);
                    }
                    else {
                        this.addLog("system", `Stopped:\n${stdout}`);
                        vscode.window.showInformationMessage("FreeAI: Services stopped");
                        this.services.forEach((s) => (s.status = "down"));
                        this.emitStatusChange();
                        resolve(true);
                    }
                });
            });
        }
        catch (e) {
            this.addLog("error", `Stop error: ${e}`);
            return false;
        }
    }
    async startService(name) {
        if (!this.workspaceRoot)
            return false;
        this.addLog("system", `Starting ${name}...`);
        try {
            const { exec } = await Promise.resolve().then(() => __importStar(require("child_process")));
            return new Promise((resolve) => {
                exec(`python "${this.launchPyPath}" ${name}`, { cwd: this.workspaceRoot }, (err, stdout) => {
                    if (err) {
                        this.addLog("error", `Start ${name} failed: ${err.message}`);
                        resolve(false);
                    }
                    else {
                        this.addLog("system", `Started ${name}`);
                        this.probeAll().then(() => this.emitStatusChange());
                        resolve(true);
                    }
                });
            });
        }
        catch {
            return false;
        }
    }
    async stopService(name) {
        if (!this.workspaceRoot)
            return false;
        this.addLog("system", `Stopping ${name}...`);
        try {
            const { exec } = await Promise.resolve().then(() => __importStar(require("child_process")));
            return new Promise((resolve) => {
                exec(`python "${this.launchPyPath}" --stop ${name}`, { cwd: this.workspaceRoot }, (err, stdout) => {
                    if (err) {
                        this.addLog("error", `Stop ${name} failed: ${err.message}`);
                        resolve(false);
                    }
                    else {
                        this.addLog("system", `Stopped ${name}`);
                        const svc = this.services.find((s) => s.name === name);
                        if (svc) {
                            svc.status = "down";
                            this.emitStatusChange();
                        }
                        resolve(true);
                    }
                });
            });
        }
        catch {
            return false;
        }
    }
    getDebugLogs() {
        return [...this.debugLogs];
    }
    getLogs() {
        return this.debugLogs;
    }
    clearLogs() {
        this.debugLogs = [];
    }
    setMockMode(enabled) {
        this.mockMode = enabled;
        this.addLog("system", `MOCK_LLM mode ${enabled ? "ENABLED" : "DISABLED"}`);
    }
    isMockMode() {
        return this.mockMode;
    }
    addLog(type, message, data) {
        this.debugLogs.push({ ts: new Date().toISOString(), type, message, data });
        if (this.debugLogs.length > 500)
            this.debugLogs.shift();
    }
}
exports.ServiceManager = ServiceManager;
//# sourceMappingURL=services.js.map