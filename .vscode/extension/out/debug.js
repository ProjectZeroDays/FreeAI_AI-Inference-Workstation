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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const services_1 = require("./services");
const router_1 = require("./router");
let serviceManager;
let routerClient;
function activate(context) {
    serviceManager = new services_1.ServiceManager(context);
    routerClient = new router_1.RouterClient(serviceManager);
    context.subscriptions.push(vscode.commands.registerCommand("freeai.debug.toggleMock", async () => {
        const current = serviceManager.isMockMode();
        serviceManager.setMockMode(!current);
        vscode.window.showInformationMessage(`FreeAI: MOCK_LLM=${!current ? "1 (enabled)" : "0 (disabled)"}`);
    }), vscode.commands.registerCommand("freeai.debug.viewLogs", () => {
        const logs = serviceManager.getLogs();
        if (!logs.length) {
            vscode.window.showInformationMessage("FreeAI: No debug logs");
            return;
        }
        const content = logs.map((l) => `## ${l.ts} [${l.type.toUpperCase()}]\n${l.message}${l.data ? "\n```\n" + JSON.stringify(l.data, null, 2) + "\n```" : ""}`).join("\n\n---\n\n");
        const doc = vscode.workspace.createTextDocument("debug-log.md", content);
        vscode.window.showTextDocument(doc);
    }), vscode.commands.registerCommand("freeai.debug.clearLogs", () => {
        serviceManager.clearLogs();
        vscode.window.showInformationMessage("FreeAI: Debug logs cleared");
    }), vscode.commands.registerCommand("freeai.debug.showMetrics", async () => {
        try {
            const metrics = await routerClient.getMetrics();
            const doc = await vscode.workspace.openTextDocument({
                content: JSON.stringify(metrics, null, 2),
                language: "json",
            });
            await vscode.window.showTextDocument(doc);
        }
        catch (e) {
            vscode.window.showErrorMessage(`FreeAI: Failed to fetch metrics: ${e}`);
        }
    }), vscode.commands.registerCommand("freeai.debug.showModels", async () => {
        try {
            const models = await routerClient.getModels();
            const lines = Object.entries(models).map(([k, v]) => `- ${k}: ${v.name || k} [${v.role || "unknown"}]`).join("\n");
            vscode.window.showInformationMessage(`FreeAI Models:\n${lines || "(none loaded)"}`);
        }
        catch (e) {
            vscode.window.showErrorMessage(`FreeAI: Failed to fetch models: ${e}`);
        }
    }), vscode.commands.registerCommand("freeai.debug.showProviders", async () => {
        try {
            const providers = await routerClient.getProviders();
            const lines = providers.map((p) => `- ${p.name} (${p.style}) ${p.enabled ? "enabled" : "disabled"} key:${p.keyed ? "yes" : "no"}`).join("\n");
            vscode.window.showInformationMessage(`FreeAI Providers:\n${lines || "(none loaded)"}`);
        }
        catch (e) {
            vscode.window.showErrorMessage(`FreeAI: Failed to fetch providers: ${e}`);
        }
    }));
}
function deactivate() { }
//# sourceMappingURL=debug.js.map