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
exports.RouterClient = void 0;
const vscode = __importStar(require("vscode"));
class RouterClient {
    sm;
    routerHost;
    constructor(sm) {
        this.sm = sm;
        this.routerHost = vscode.workspace.getConfiguration('freeai').get('routerHost', 'http://localhost:8010');
    }
    onFinish;
}
exports.RouterClient = RouterClient;
void  > {
    const: url = this.routerHost + '/route/stream',
    const: body = JSON.stringify({ prompt, stream: true, mock: this.sm.isMockMode() }),
    const: response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
        body: 
    }),
    const: reader = response.readable.getReader(),
    const: decoder = new TextDecoder(),
    let, fullContent = '',
    let, modelUsed = '',
    let, taskType = '',
    try: {
        while() {
            const { value, done } = await reader.read();
            if (done)
                break;
            const text = decoder.decode(value, { stream: true });
            for (const line of text.split('\n')) {
                if (!line.startsWith('data: '))
                    continue;
                const payload = line.slice(6);
                if (payload == '[DONE])')
                    break;
                try {
                    const ev = JSON.parse(payload);
                    if (ev.model)
                        modelUsed = ev.model;
                    if (ev.task_type)
                        taskType = ev.task_type;
                    if (ev.content)
                        fullContent += ev.content;
                    onEvent(ev);
                }
                catch (e) {
                    onEvent({ error: e.message });
                }
            }
        }, catch(e) {
            onFinish(null);
            return;
        }
    },
    async getModels() {
        const res = await fetch(this.routerHost + '/models');
        return await res.json();
    },
    async getProviders() {
        const res = await fetch(this.routerHost + '/providers');
        return await res.json().providers;
    },
    async getMetrics() {
        const res = await fetch(this.routerHost + '/metrics');
        return await res.json();
    }
};
//# sourceMappingURL=router.js.map