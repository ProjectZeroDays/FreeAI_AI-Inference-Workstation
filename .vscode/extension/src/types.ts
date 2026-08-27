export interface ServiceStatus {
  name: string;
  port: number;
  status: "ok" | "degraded" | "down";
  latencyMs?: number;
  priority: "critical" | "high" | "medium" | "low";
  healthPath?: string | null;
  dependencies: string[];
  pid?: number;
  module?: string;
}

export interface RouterResponse {
  model_used?: string;
  task_type?: string;
  confidence?: number;
  elapsed_ms?: number;
  response?: Record<string, unknown>;
  error?: string;
}

export interface RouterStreamEvent {
  model?: string;
  task_type?: string;
  content?: string;
  error?: string;
}

export interface DebugLog {
  ts: string;
  type: "request" | "response" | "error" | "system";
  message: string;
  data?: unknown;
}
