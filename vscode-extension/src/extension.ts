import * as vscode from "vscode";
import { FreeAIClient } from "./client";
import { StatusBar } from "./statusBar";

let statusBar: StatusBar | undefined;
let client: FreeAIClient | undefined;

export function activate(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("freeai");
  const apiBaseUrl = config.get<string>("apiBaseUrl") ?? "http://localhost:8000";
  const intervalMs = config.get<number>("refreshIntervalMs") ?? 10000;

  client = new FreeAIClient(apiBaseUrl);
  statusBar = new StatusBar(client, intervalMs);
  statusBar.show();

  context.subscriptions.push(
    vscode.commands.registerCommand("freeai.status", async () => {
      await showStatusPanel();
    }),
    vscode.commands.registerCommand("freeai.route", async () => {
      await executeRoute();
    }),
    vscode.commands.registerCommand("freeai.agents", async () => {
      await showAgentsPanel();
    }),
    vscode.commands.registerCommand("freeai.logs", async () => {
      await showLogsPanel();
    }),
    vscode.commands.registerCommand("freeai.refreshStatus", async () => {
      await statusBar?.refresh();
    }),
    vscode.commands.registerCommand("freeai.setStatusBar", async (baseUrl: string) => {
      if (baseUrl) {
        client?.setBaseUrl(baseUrl);
        await statusBar?.refresh();
        vscode.window.showInformationMessage(`FreeAI: API base set to ${baseUrl}`);
      }
    })
  );
}

export function deactivate() {
  statusBar?.dispose();
}

async function showStatusPanel(): Promise<void> {
  const panel = createPanel("FreeAI Service Status", "freeaiStatus");
  async function render(): Promise<void> {
    try {
      const health = await client!.health();
      const services = health.services ?? {};
      const entries = Object.entries(services);
      if (entries.length === 0) {
        panel.webview.html = buildStatusHtml(
          health.ok !== false ? "up" : "unknown",
          entries,
          panel.webview
        );
        return;
      }
      panel.webview.html = buildStatusHtml(
        entries.every(([, s]) => s.status === "up" || s.status === "healthy") ? "up" : "degraded",
        entries,
        panel.webview
      );
    } catch (err) {
      panel.webview.html = buildStatusHtml("error", [], panel.webview, String(err));
    }
  }
  await render();
  panel.onDidReceiveMessage(async (msg) => {
    if (msg.command === "refresh") await render();
  });
}

async function executeRoute(): Promise<void> {
  const prompt = await vscode.window.showInputBox({
    placeHolder: "Enter your prompt...",
    ignoreFocusOut: true,
    validateInput: (v) => (v && v.trim() ? null : "Prompt cannot be empty"),
  });
  if (!prompt) return;

  const panel = createPanel("FreeAI Route", "freeaiRoute");
  panel.webview.html = buildRouteHtml(prompt, "", null, null, panel.webview);

  try {
    const result = await client!.route(prompt);
    const content = result.response?.content ?? result.content ?? JSON.stringify(result, null, 2);
    panel.webview.html = buildRouteHtml(
      prompt,
      String(content),
      result.model_used ?? result.model ?? null,
      result.task_type ?? null,
      panel.webview
    );
  } catch (err) {
    panel.webview.html = buildRouteHtml(prompt, "", String(err), null, panel.webview);
  }
}

async function showAgentsPanel(): Promise<void> {
  const panel = createPanel("FreeAI Agents", "freeaiAgents");
  try {
    const data = await client!.agents();
    panel.webview.html = buildAgentsHtml(data, panel.webview);
  } catch (err) {
    panel.webview.html = buildAgentsHtml({ agents: {}, list: [] }, panel.webview, String(err));
  }
}

async function showLogsPanel(): Promise<void> {
  const panel = createPanel("FreeAI Logs", "freeaiLogs");

  const countResult = await vscode.window.showInputBox({
    placeHolder: "Number of log lines (default 100)",
    ignoreFocusOut: true,
    value: "100",
  });
  const lines = countResult ? parseInt(countResult, 10) : 100;

  panel.webview.html = buildLogsHtml([], `Fetching ${lines} lines...`, panel.webview);

  try {
    const data = await client!.logs({ lines: isNaN(lines) ? 100 : lines });
    const entries = data.entries ?? [];
    panel.webview.html = buildLogsHtml(entries, null, panel.webview);
  } catch (err) {
    panel.webview.html = buildLogsHtml([], String(err), panel.webview);
  }
}

function createPanel(title: string, viewType: string): vscode.WebviewPanel {
  const panel = vscode.window.createWebviewPanel(
    viewType,
    title,
    vscode.ViewColumn.Two,
    { enableScripts: true, retainContextWhenHidden: true }
  );
  return panel;
}

function buildStatusHtml(
  overall: string,
  services: [string, { status: string; latencyMs?: number }][],
  webview: vscode.Webview,
  error?: string
): string {
  const csp = webview.cspSource;
  const rows = services.map(([name, s]) => {
    const dot = s.status === "up" || s.status === "healthy" ? "ok"
      : s.status === "down" || s.status === "unhealthy" ? "down" : "degraded";
    return `<tr>
      <td><span class="dot dot-${dot}"></span>${esc(name)}</td>
      <td class="meta">${esc(s.status)}</td>
      <td class="meta">${s.latencyMs != null ? `${s.latencyMs}ms` : ""}</td>
    </tr>`;
  }).join("");

  const overallClass = overall === "up" ? "ok" : overall === "error" ? "error" : "degraded";
  return `<!DOCTYPE html>
<html><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src '${csp}' 'unsafe-inline'; script-src '${csp}';">
<style>
body{background:#1e1e1e;color:#d4d4d4;font-family:'Segoe UI',sans-serif;padding:16px}
.header{font-size:16px;font-weight:600;margin-bottom:12px;color:#4ec9b0}
.meta{color:#808080;font-size:11px}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:6px 8px;border-bottom:1px solid #3e3e42;color:#808080;font-size:11px;text-transform:uppercase}
td{padding:6px 8px;border-bottom:1px solid #2d2d30;font-size:13px}
tr:hover{background:#2a2d2e}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.dot-ok{background:#26a64a}.dot-down{background:#f97583}.dot-degraded{background:#e5a500}
.error-box{color:#f97583;background:#3d2020;padding:10px;border-radius:4px;margin-bottom:12px}
.refresh-btn{background:#0e639c;color:white;border:none;padding:4px 12px;border-radius:2px;cursor:pointer;font-size:12px}
.refresh-btn:hover{background:#1177bb}
</style></head>
<body>
<div class="header">FreeAI Service Status <span class="dot dot-${overallClass}"></span></div>
<div class="meta">${services.length} services · ${new Date().toLocaleTimeString()}</div>
${error ? `<div class="error-box">${esc(error)}</div>` : ""}
<table>
<thead><tr><th>Service</th><th>Status</th><th>Latency</th></tr></thead>
<tbody>${rows || "<tr><td colspan='3' class='meta'>No services responding</td></tr>"}</tbody>
</table>
<button class="refresh-btn" onclick="vscode.postMessage({command:'refresh'})">Refresh</button>
</body></html>`;
}

function buildRouteHtml(
  prompt: string,
  content: string,
  error: string | null,
  model: string | null,
  webview: vscode.Webview
): string {
  const csp = webview.cspSource;
  return `<!DOCTYPE html>
<html><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src '${csp}' 'unsafe-inline'; script-src '${csp}';">
<style>
body{background:#1e1e1e;color:#d4d4d4;font-family:'Segoe UI',sans-serif;padding:20px;max-width:800px}
.prompt{background:#2d2d30;border-left:3px solid #0e639c;padding:10px 14px;margin-bottom:16px;border-radius:0 4px 4px 0}
.prompt-label{font-size:11px;color:#808080;text-transform:uppercase;margin-bottom:4px}
.content{background:#252526;border:1px solid #3e3e42;padding:14px;border-radius:4px;white-space:pre-wrap;font-size:14px;line-height:1.6;max-height:500px;overflow-y:auto}
.meta{margin-top:12px;font-size:11px;color:#808080;display:flex;gap:16px;flex-wrap:wrap}
.meta span{background:#2d2d30;padding:2px 8px;border-radius:3px}
.error{color:#f97583;background:#3d2020;border:1px solid #f97583;padding:10px;border-radius:4px;margin-top:12px}
</style></head>
<body>
<div class="prompt"><div class="prompt-label">Prompt</div>${esc(prompt)}</div>
${error ? `<div class="error">Error: ${esc(error)}</div>` : `<div class="content">${esc(content)}</div>`}
<div class="meta">
${model ? `<span>Model: ${esc(model)}</span>` : ""}
<span>${new Date().toLocaleTimeString()}</span>
</div>
</body></html>`;
}

function buildAgentsHtml(
  data: { agents?: Record<string, { model: string; description?: string }>; list?: string[] },
  webview: vscode.Webview,
  error?: string | null
): string {
  const csp = webview.cspSource;
  const agents = data.agents ?? {};
  const list = data.list ?? [];
  const all = list.length > 0 ? list.map((n) => ({ name: n, model: "", description: "" }))
    : Object.entries(agents).map(([name, info]) => ({ name, model: info.model ?? "", description: info.description ?? "" }));

  const rows = all.map((a) =>
    `<tr><td>${esc(a.name)}</td><td class="meta">${esc(a.model || "—")}</td><td class="meta">${esc(a.description || "")}</td></tr>`
  ).join("");

  return `<!DOCTYPE html>
<html><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src '${csp}' 'unsafe-inline'; script-src '${csp}';">
<style>
body{background:#1e1e1e;color:#d4d4d4;font-family:'Segoe UI',sans-serif;padding:16px}
.header{font-size:16px;font-weight:600;margin-bottom:12px;color:#4ec9b0}
.meta{color:#808080;font-size:11px}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:6px 8px;border-bottom:1px solid #3e3e42;color:#808080;font-size:11px;text-transform:uppercase}
td{padding:6px 8px;border-bottom:1px solid #2d2d30;font-size:13px}
tr:hover{background:#2a2d2e}
.error{color:#f97583;background:#3d2020;padding:10px;border-radius:4px}
</style></head>
<body>
<div class="header">FreeAI Agents (${all.length})</div>
${error ? `<div class="error">${esc(error)}</div>` : ""}
<table>
<thead><tr><th>Agent</th><th>Model</th><th>Description</th></tr></thead>
<tbody>${rows || "<tr><td colspan='3' class='meta'>No agents found</td></tr>"}</tbody>
</table>
</body></html>`;
}

function buildLogsHtml(
  entries: string[],
  error: string | null,
  webview: vscode.Webview
): string {
  const csp = webview.cspSource;
  const lines = entries.map((e) => `<div class="line">${esc(e)}</div>`).join("");
  return `<!DOCTYPE html>
<html><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src '${csp}' 'unsafe-inline'; script-src '${csp}';">
<style>
body{background:#1e1e1e;color:#d4d4d4;font-family:'Courier New',monospace;font-size:12px;padding:16px}
.header{font-size:16px;font-weight:600;margin-bottom:12px;color:#4ec9b0}
.line{padding:1px 0;border-bottom:1px solid #2d2d30;white-space:pre-wrap;word-break:break-all}
.error{color:#f97583;background:#3d2020;padding:10px;border-radius:4px;margin-bottom:12px}
</style></head>
<body>
<div class="header">FreeAI Logs (${entries.length} lines)</div>
${error ? `<div class="error">${esc(error)}</div>` : ""}
<div class="lines">${lines || "<div class='meta'>No logs available</div>"}</div>
</body></html>`;
}

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
