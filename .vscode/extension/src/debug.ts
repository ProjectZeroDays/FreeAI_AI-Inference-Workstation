import * as vscode from "vscode";
import { ServiceManager } from "./services";
import { RouterClient } from "./router";

let serviceManager: ServiceManager;
let routerClient: RouterClient;

export function activate(context: vscode.ExtensionContext) {
  serviceManager = new ServiceManager(context);
  routerClient = new RouterClient(serviceManager);

  context.subscriptions.push(
    vscode.commands.registerCommand("freeai.debug.toggleMock", async () => {
      const current = serviceManager.isMockMode();
      serviceManager.setMockMode(!current);
      vscode.window.showInformationMessage(
        `FreeAI: MOCK_LLM=${!current ? "1 (enabled)" : "0 (disabled)"}`,
      );
    }),
    vscode.commands.registerCommand("freeai.debug.viewLogs", () => {
      const logs = serviceManager.getLogs();
      if (!logs.length) {
        vscode.window.showInformationMessage("FreeAI: No debug logs");
        return;
      }
      const content = logs.map((l) =>
        `## ${l.ts} [${l.type.toUpperCase()}]\n${l.message}${l.data ? "\n```\n" + JSON.stringify(l.data, null, 2) + "\n```" : ""}`
      ).join("\n\n---\n\n");
      const doc = vscode.workspace.createTextDocument("debug-log.md", content);
      vscode.window.showTextDocument(doc);
    }),
    vscode.commands.registerCommand("freeai.debug.clearLogs", () => {
      serviceManager.clearLogs();
      vscode.window.showInformationMessage("FreeAI: Debug logs cleared");
    }),
    vscode.commands.registerCommand("freeai.debug.showMetrics", async () => {
      try {
        const metrics = await routerClient.getMetrics();
        const doc = await vscode.workspace.openTextDocument({
          content: JSON.stringify(metrics, null, 2),
          language: "json",
        });
        await vscode.window.showTextDocument(doc);
      } catch (e) {
        vscode.window.showErrorMessage(`FreeAI: Failed to fetch metrics: ${e}`);
      }
    }),
    vscode.commands.registerCommand("freeai.debug.showModels", async () => {
      try {
        const models = await routerClient.getModels();
        const lines = Object.entries(models).map(([k, v]: [string, any]) =>
          `- ${k}: ${(v as any).name || k} [${(v as any).role || "unknown"}]`
        ).join("\n");
        vscode.window.showInformationMessage(`FreeAI Models:\n${lines || "(none loaded)"}`);
      } catch (e) {
        vscode.window.showErrorMessage(`FreeAI: Failed to fetch models: ${e}`);
      }
    }),
    vscode.commands.registerCommand("freeai.debug.showProviders", async () => {
      try {
        const providers = await routerClient.getProviders();
        const lines = providers.map((p: any) =>
          `- ${p.name} (${p.style}) ${p.enabled ? "enabled" : "disabled"} key:${p.keyed ? "yes" : "no"}`
        ).join("\n");
        vscode.window.showInformationMessage(`FreeAI Providers:\n${lines || "(none loaded)"}`);
      } catch (e) {
        vscode.window.showErrorMessage(`FreeAI: Failed to fetch providers: ${e}`);
      }
    }),
  );
}

export function deactivate() { }
