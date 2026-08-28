export class FreeAIClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? "http://localhost:8000";
  }

  get baseUrlValue(): string {
    return this.baseUrl;
  }

  setBaseUrl(url: string): void {
    this.baseUrl = url;
  }

  async get<T>(path: string): Promise<T> {
    const url = this.resolve(path);
    const resp = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status} from ${url}`);
    }
    return resp.json() as Promise<T>;
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const url = this.resolve(path);
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    if (!resp.ok) {
      const errText = await resp.text().catch(() => "");
      throw new Error(`HTTP ${resp.status} from ${url}: ${errText.slice(0, 200)}`);
    }
    return resp.json() as Promise<T>;
  }

  resolve(path: string): string {
    const base = this.baseUrl.replace(/\/$/, "");
    const p = path.replace(/^\/+/, "");
    return `${base}/${p}`;
  }

  async health(): Promise<{ ok?: boolean; uptime?: number; services?: Record<string, { status: string; latencyMs?: number }> }> {
    return this.get("/health");
  }

  async route(prompt: string, options?: { max_tokens?: number; profile?: string }): Promise<Record<string, unknown>> {
    return this.post("/route", { prompt, ...options });
  }

  async agents(): Promise<{ agents?: Record<string, { model: string; description?: string }>; list?: string[] }> {
    return this.get("/agents");
  }

  async logs(options?: { lines?: number; tail?: number }): Promise<{ entries?: string[]; count?: number }> {
    const params = new URLSearchParams();
    if (options?.lines) params.set("lines", String(options.lines));
    if (options?.tail) params.set("tail", String(options.tail));
    const query = params.toString();
    return this.get(`/logs${query ? `?${query}` : ""}`);
  }
}
