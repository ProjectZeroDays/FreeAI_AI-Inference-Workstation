import * as vscode from "vscode";
import { FreeAIClient } from "./client";

const HEALTH_ICON_UP = "$(check-all)";
const HEALTH_ICON_DEGRADED = "$(warning)";
const HEALTH_ICON_DOWN = "$(error)";

export class StatusBar {
  private item: vscode.StatusBarItem;
  private client: FreeAIClient;
  private pollingTimer: NodeJS.Timeout | undefined;
  private intervalMs: number;

  constructor(client: FreeAIClient, intervalMs: number) {
    this.client = client;
    this.intervalMs = intervalMs;
    this.item = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.item.tooltip = "FreeAI: Click for service status";
    this.item.command = "freeai.status";
  }

  show(): void {
    this.item.show();
    this.refresh();
    this.startPolling();
  }

  dispose(): void {
    this.stopPolling();
    this.item.dispose();
  }

  async refresh(): Promise<void> {
    try {
      const health = await this.client.health();
      const services = health.services ?? {};
      const entries = Object.entries(services);
      if (entries.length === 0) {
        const ok = health.ok !== false;
        this.setItem(ok ? HEALTH_ICON_UP : HEALTH_ICON_DOWN, ` FreeAI: ${ok ? "up" : "checking..."}`);
        return;
      }
      const up = entries.filter(([, s]) => s.status === "up" || s.status === "healthy").length;
      const down = entries.filter(([, s]) => s.status === "down" || s.status === "unhealthy").length;
      const degraded = entries.length - up - down;
      if (down === 0 && degraded === 0) {
        this.setItem(
          HEALTH_ICON_UP,
          ` FreeAI: ${up}/${entries.length} services healthy`
        );
      } else if (down === 0) {
        this.setItem(
          HEALTH_ICON_DEGRADED,
          ` FreeAI: ${degraded} degraded · ${up}/${entries.length} up`
        );
      } else {
        this.setItem(
          HEALTH_ICON_DOWN,
          ` FreeAI: ${down} down · ${degraded} degraded`
        );
      }
    } catch {
      this.setItem(HEALTH_ICON_DOWN, " FreeAI: unreachable");
    }
  }

  private setItem(icon: string, text: string): void {
    this.item.text = `${icon} ${text}`;
    this.item.tooltip = text;
  }

  private startPolling(): void {
    this.stopPolling();
    this.pollingTimer = setInterval(() => this.refresh(), this.intervalMs);
  }

  private stopPolling(): void {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = undefined;
    }
  }
}
