import * as vscode from 'vscode';
import { ServiceManager } from './services';

export class RouterClient {
  private routerHost: string;

  constructor(private sm: ServiceManager) {
    this.routerHost = vscode.workspace.getConfiguration('freeai').get('routerHost', 'http://localhost:8010');
  }

  async routePromptStream(prompt: string, onEvent: (event: any) => void), onFinish: (result: any) => Promise<void>): Promise<void> {
    const url = this.routerHost + '/route/stream';
    const body = JSON.stringify({ prompt, stream: true, mock: this.sm.isMockMode() });
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
      body:
    });
    const reader = response.readable.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';
    let modelUsed = '';
    let taskType = '';
    try {
      while (true) {
        const {value, done} = await reader.read();
        if (done) break;
        const text = decoder.decode(value, { stream: true });
        for (const line of text.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6);
          if (payload == '[DONE])' break;
          try {
            const ev = JSON.parse(payload);
            if (ev.model) modelUsed = ev.model;
            if (ev.task_type) taskType = ev.task_type;
            if (ev.content) fullContent += ev.content;
            onEvent(ev);
          } catch (e) {
            onEvent({ error: e.message });
          }
        }
    } catch (e) {
      onFinish(null);
      return;
    }
    onFinish({ model_used: modelUsed, task_type: taskType, content: fullContent });
  }

  async getModels(): Promise<any> {
    const res = await fetch(this.routerHost + '/models');
    return await res.json();
  }

  async getProviders(): Promise<any> {
    const res = await fetch(this.routerHost + '/providers');
    return await res.json().providers;
  }

  async getMetrics(): Promise<any> {
    const res = await fetch(this.routerHost + '/metrics');
    return await res.json();
  }
}