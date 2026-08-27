import * as vscode from "vscode";
import * as net from "net";
import * as http from "http";
import * as path from "path";
import * as fs from "fs";
import { ServiceManager } from "./services";
import { RouterClient } from "./router";

let statusBarItem: vscode.StatusBarItem;
let serviceManager: ServiceManager;
let routerClient: RouterClient;
let currentPanel: vscode.WebviewPanel | null = null;

export function activate(context: vscode.ExtensionContext) {
  serviceManager = new ServiceManager(context);
  routerClient = new RouterClient(serviceManager);

  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.tooltip = "FreeAI Workspace -- click for status";
  context.subscriptions.push(statusBarItem);

  registerCommands(context);

  statusBarItem.text = "$(loading~spin) FreeAI: Detecting...";
  statusBarItem.show();

  initialize().then(() => {
    serviceManager.startPolling();
    updateStatusBar();
  });

  const autoStart = vscode.workspace.getConfiguration("freeai").get<boolean>("autoStart", false);
  if (autoStart) {
    serviceManager.startServices();
  }
}

async function initialize(): Promise<void> {
  await serviceManager.loadServices();
  updateStatusBar();
}

function registerCommands(context: vscode.ExtensionContext): void {
  context.subscriptions.push(
    vscode.commands.registerCommand("freeai.status", async () => {
      await serviceManager.loadServices();
      await serviceManager.probeAll();
      updateStatusBar();
      showStatusPanel();
    }),
    vscode.commands.registerCommand("freeai.route", async () => {
      await executeRoute();
    }),
    vscode.commands.registerCommand("freeai.start", async () => {
      await serviceManager.startServices();
    }),
    vscode.commands.registerCommand("freeai.stop", async () => {
      await serviceManager.stopServices();
    }),
    vscode.commands.registerCommand("freeai.refresh", async () => {
      await serviceManager.probeAll();
      updateStatusBar();
      if (currentPanel) refreshPanel();
    }),
    vscode.commands.registerCommand("freeai.toggleMock", async () => {
      const current = serviceManager.isMockMode();
      serviceManager.setMockMode(!current);
      vscode.window.showInformationMessage(
        `FreeAI: Mock LLM mode ${!current ? "ENABLED" : "DISABLED"}`,
      );
    }),
    vscode.commands.registerCommand("freeai.clearLogs", async () => {
      serviceManager.clearLogs();
      vscode.window.showInformationMessage("FreeAI: Debug logs cleared");
    }),
    vscode.commands.registerCommand("freeai.startService", async (name: string) => {
      await serviceManager.startService(name);
      if (currentPanel) refreshPanel();
    }),
    vscode.commands.registerCommand("freeai.stopService", async (name: string) => {
      await serviceManager.stopService(name);
      if (currentPanel) refreshPanel();
    }),
  );
}

async function executeRoute(): Promise<void> {
  const prompt = await vscode.window.showInputBox({
    placeHolder: "Enter your prompt...",
    ignoreFocusOut: true,
    validateInput: (v) => (v && v.trim() ? null : "Prompt cannot be empty"),
  });
  if (!prompt) return;

  const mockMode = serviceManager.isMockMode();
  if (mockMode) {
    vscode.window.showInformationMessage("FreeAI: Routing in MOCK mode");
  }

  const panel = createChatPanel();
  appendToPanel(panel, "system", `Sending: ${prompt.slice(0, 100)}${prompt.length > 100 ? "..." : ""}`);

  let fullContent = "";
  let modelUsed = "";
  let taskType = "";
  const startTime = Date.now();

  await routerClient.routePromptStream(
    prompt,
    (event) => {
      if (event.model && !modelUsed) {
        modelUsed = event.model;
        appendToPanel(panel, "system", `Model: ${modelUsed}`);
      }
      if (event.task_type && !taskType) {
        taskType = event.task_type;
        appendToPanel(panel, "system", `Task: ${taskType}`);
      }
      if (event.content) {
        fullContent += event.content;
        updateStreamingContent(panel, fullContent);
      }
      if (event.error) {
        appendToPanel(panel, "system", `Error: ${event.error}`);
      }
    },
    async (result) => {
      if (!result) {
        const elapsed = Date.now() - startTime;
        const contentStr = fullContent.trim();
        const tokenCount = contentStr.split(/\s+/).filter(Boolean).length;
        panel.webview.html = buildChatHtml(
          prompt, fullContent, modelUsed, taskType, elapsed, tokenCount, null,
        );
        return;
      }
      const elapsed = Date.now() - startTime;
      const respContent = result.response?.content || JSON.stringify(result.response || {});
      const tokenCount = String(respContent).split(/\s+/).filter(Boolean).length;
      panel.webview.html = buildChatHtml(
        prompt, respContent,
        result.model_used || modelUsed,
        result.task_type || taskType,
        elapsed,
        tokenCount,
        result.error,
      );
    },
  );
}

function createChatPanel(): vscode.WebviewPanel {
  if (currentPanel && currentPanel.disposed) {
    currentPanel = null;
  }
  if (!currentPanel) {
    currentPanel = vscode.window.createWebviewPanel(
      "freeaiChat",
      "FreeAI Chat",
      vscode.ViewColumn.Two,
      { enableScripts: true, retainContextWhenHidden: true },
    );
    currentPanel.onDidDispose(() => { currentPanel = null; });
  }
  return currentPanel;
}

function appendToPanel(panel: vscode.WebviewPanel, role: string, text: string): void {
  panel.webview.postMessage({ type: "append", role, text: escapeHtml(text) });
}

function updateStreamingContent(panel: vscode.WebviewPanel, content: string): void {
  panel.webview.postMessage({ type: "stream", content: escapeHtml(content) });
}

function showStatusPanel(): void {
  const panel = vscode.window.createWebviewPanel(
    "freeaiStatus",
    "FreeAI Service Status",
    vscode.ViewColumn.One,
    { enableScripts: true },
  );
  const services = serviceManager.getServices();
  panel.webview.html = buildStatusHtml(panel.webview, services);
}

function refreshPanel(): void {
  if (!currentPanel) return;
  const services = serviceManager.getServices();
  currentPanel.webview.html = buildStatusHtml(currentPanel.webview, services);
}

function buildStatusHtml(webview: vscode.Webview, services: Array<{ name: string; port: number; status: string; latencyMs?: number; priority: string }>): string {
  const rows = services.map((s) => {
    const dotClass = s.status === "ok" ? "dot-ok" : s.status === "degraded" ? "dot-degraded" : "dot-down";
    const prioClass = `priority-${s.priority}`;
    const latencyStr = s.latencyMs != null ? ` ${s.latencyMs}ms` : "";
    return `<tr>
      <td><span class="dot ${dotClass}"></span>${s.name}</td>
      <td class="meta">:${s.port}</td>
      <td class="${prioClass}">${s.priority}</td>
      <td>${s.status.toUpperCase()}<span class="meta">${latencyStr}</span></td>
      <td class="actions">
        <button onclick="vscode.postMessage({cmd:'start',name:'${s.name}'})">Start</button>
        <button onclick="vscode.postMessage({cmd:'stop',name:'${s.name}'})">Stop</button>
      </td>
    </tr>`;
  }).join("");

  const up = services.filter((s) => s.status === "ok").length;
  return `<!DOCTYPE html>
<html><head><style>
body { background: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', sans-serif; padding: 16px; }
.header { font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #4ec9b0; }
.meta { color: #808080; font-size: 11px; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 6px 8px; border-bottom: 1px solid #3e3e42; color: #808080; font-size: 11px; text-transform: uppercase; }
td { padding: 6px 8px; border-bottom: 1px solid #2d2d30; font-size: 13px; }
tr:hover { background: #2a2d2e; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-ok { background: #26a64a; }
.dot-down { background: #f97583; }
.dot-degraded { background: #e5a500; }
.priority-critical { color: #f97583; }
.priority-high { color: #ce9178; }
.priority-medium { color: #dcdcaa; }
.priority-low { color: #808080; }
.actions button { background: #0e639c; color: white; border: none; padding: 2px 8px; margin: 0 2px; cursor: pointer; border-radius: 2px; font-size: 11px; }
.actions button:hover { background: #1177bb; }
</style></head>
<body>
<div class="header">FreeAI -- Service Health</div>
<div class="meta">${up}/${services.length} services UP · ${new Date().toLocaleTimeString()}</div>
<table>
<thead><tr><th>Service</th><th>Port</th><th>Priority</th><th>Status</th><th>Actions</th></tr></thead>
<tbody>${rows}</tbody>
</table>
<script>
const vscode = acquireVsCodeApi();
window.addEventListener('message', e => {
  if (e.data.cmd === 'refresh') showStatusPanel();
});
</script>
</body></html>`;
}

function buildChatHtml(
  prompt: string,
  content: string,
  model: string,
  taskType: string,
  elapsed: number,
  tokens: number,
  error: string | null,
): string {
  return `<!DOCTYPE html>
<html><head><style>
body { background: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', sans-serif; padding: 20px; max-width: 800px; }
.prompt { background: #2d2d30; border-left: 3px solid #0e639c; padding: 10px 14px; margin-bottom: 16px; border-radius: 0 4px 4px 0; }
.prompt-label { font-size: 11px; color: #808080; text-transform: uppercase; margin-bottom: 4px; }
.content { background: #252526; border: 1px solid #3e3e42; padding: 14px; border-radius: 4px; white-space: pre-wrap; font-size: 14px; line-height: 1.6; max-height: 500px; overflow-y: auto; }
.meta { margin-top: 12px; font-size: 11px; color: #808080; display: flex; gap: 16px; flex-wrap: wrap; }
.meta span { background: #2d2d30; padding: 2px 8px; border-radius: 3px; }
.error { color: #f97583; background: #3d2020; border: 1px solid #f97583; padding: 10px; border-radius: 4px; margin-top: 12px; }
</style></head>
<body>
<div class="prompt"><div class="prompt-label">Prompt</div>${escapeHtml(prompt)}</div>
<div class="content">${escapeHtml(content)}</div>
${error ? `<div class="error">Error: ${escapeHtml(error)}</div>` : ""}
<div class="meta">
${model ? `<span>Model: ${escapeHtml(model)}</span>` : ""}
${taskType ? `<span>Task: ${escapeHtml(taskType)}</span>` : ""}
<span>Latency: ${elapsed}ms</span>
<span>Tokens: ~${tokens}</span>
</div>
</body></html>`;
}

function updateStatusBar(): void {
  const services = serviceManager.getServices();
  const up = services.filter((s) => s.status === "ok").length;
  const degraded = services.filter((s) => s.status === "degraded").length;
  const down = services.filter((s) => s.status === "down").length;

  if (down === 0 && degraded === 0 && up > 0) {
    statusBarItem.text = `$(check-all) FreeAI: ${up}/${services.length}`;
    statusBarItem.tooltip = `FreeAI: ${up} services healthy`;
    statusBarItem.color = undefined;
  } else if (down === 0 && degraded > 0) {
    statusBarItem.text = `$(warning) FreeAI: ${degraded} degraded`;
    statusBarItem.tooltip = `FreeAI: ${degraded} services degraded`;
    statusBarItem.color = new vscode.ThemeColor("statusBar.warningForeground");
  } else {
    statusBarItem.text = `$(error) FreeAI: ${down} down`;
    statusBarItem.tooltip = `FreeAI: ${down} services down, ${degraded} degraded`;
    statusBarItem.color = new vscode.ThemeColor("statusBar.warningForeground");
  }
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function deactivate() {
  serviceManager?.stopPolling();
  statusBarItem?.dispose();
}
