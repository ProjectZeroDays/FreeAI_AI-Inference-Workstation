/**
 * opencode plugin: rate-limit + circuit breaker + self-heal telemetry.
 *
 * This is a TEMPLATE plugin. It is deliberately conservative: it only observes
 * and records, and exposes one probe tool so agents/commands can read breaker
 * state. It does NOT mutate model provider traffic directly — in opencode the
 * clean way to rate-limit LLM calls is via provider config + agent discipline
 * (see the `rate-limit-retry` and `self-heal` skills). This plugin gives a
 * place to wire live telemetry and a breaker that future hooks can consult.
 *
 * Install: place under .opencode/plugin/ (auto-discovered *.ts/*.js) and ensure
 * `@opencode-ai/plugin` types are resolvable. After editing, quit + restart
 * opencode so the plugin reloads.
 *
 * Hook surface implemented:
 *   - event(input)          : count successes/failures per provider; drive breaker
 *   - tool.definition       : register the `ratelimit_status` probe tool
 *   - tool.execute.before   : block `bash` if breaker is open for "local"
 *
 * NOTE: the exact shape of `event` payloads depends on your opencode version.
 * Filter defensively (see isRateLimitEvent). Adjust the event-name matchers to
 * match what your version emits before relying on this in a hot loop.
 */
import type { Plugin } from "@opencode-ai/plugin";

type Provider = string;
type State = {
  rpm: number;            // tokens remaining (rpm bucket)
  tpm: number;            // tokens remaining (tpm bucket)
  lastRefill: number;     // monotonic ms
  rpmLimit: number;
  tpmLimit: number;
  // circuit breaker
  window: ("ok" | "fail")[];   // last N call outcomes
  openedUntil: number;         // monotonic ms; 0 = closed
};
const WINDOW = 10;
const BREAK_THRESHOLD = 5;      // >=5 fails in last 10 -> open
const OPEN_DURATION_MS = 60_000;

const states = new Map<Provider, State>();

function ensure(p: Provider): State {
  let s = states.get(p);
  if (!s) {
    s = {
      rpm: 60, tpm: 30_000, lastRefill: Date.now(),
      rpmLimit: 60, tpmLimit: 30_000,
      window: [], openedUntil: 0,
    };
    states.set(p, s);
  }
  return s;
}

function isOpen(p: Provider): boolean {
  const s = ensure(p);
  if (s.openedUntil && Date.now() < s.openedUntil) return true;
  if (s.openedUntil && Date.now() >= s.openedUntil) {
    s.openedUntil = 0; // half-open: let the next call probe
  }
  return false;
}

function record(p: Provider, ok: boolean) {
  const s = ensure(p);
  s.window.push(ok ? "ok" : "fail");
  if (s.window.length > WINDOW) s.window.shift();
  const fails = s.window.filter((x) => x === "fail").length;
  if (!ok && fails >= BREAK_THRESHOLD) {
    s.openedUntil = Date.now() + OPEN_DURATION_MS;
  } else if (ok) {
    // on a success, slowly close the window
    if (s.window.length === WINDOW && fails === 0) s.openedUntil = 0;
  }
}

function isRateLimitEvent(input: unknown): { provider: string; ok: boolean } | null {
  // Defensive shape check. opencode emits various event kinds; the ones we care
  // about are model/tool call completions. Adapt these field names to your
  // opencode version if needed.
  const e = input as Record<string, unknown> | null;
  if (!e || typeof e !== "object") return null;
  const type = e.type ?? e.event ?? e.kind;
  if (typeof type !== "string" || !type) return null;
  // Match completion-style events.
  const isCompletion = /completion|chat\.message|tool\.execute\.after|model/i.test(type);
  if (!isCompletion) return null;
  const modelRaw = e.model;
  const provider =
    (typeof e.provider === "string" && e.provider) ||
    (typeof modelRaw === "string" ? modelRaw.split("/")[0] : "") ||
    "unknown";
  const status = typeof e.status === "number" ? e.status : undefined;
  const ok =
    e.error == null &&
    e.ok !== false &&
    e.success !== false &&
    status !== 429 &&
    (status === undefined || status < 500);
  return { provider, ok: Boolean(ok) };
}

export default (async ({ }) => {
  return {
    // Observe every bus event to feed the breaker per provider.
    event(input: unknown) {
      const r = isRateLimitEvent(input);
      if (r) record(r.provider, r.ok);
    },

    // Register a probe tool so agents/skills can read breaker + bucket state.
    "tool.definition": {
      ratelimit_status: {
        description:
          "Read the live rate-limit/circuit-breaker state tracked by the rate-limit plugin. " +
          "Returns per-provider bucket tokens, last window outcomes, and breaker open/closed status. " +
          "Call before planning a burst of subagent dispatches.",
        parameters: {
          type: "object",
          properties: {
            provider: { type: "string", description: "Filter to one provider; omit for all" },
          },
        },
      },
    },

    // Implement the probe tool.
    "tool.execute.before": async (input, output) => {
      const tool = (input?.tool ?? output?.tool) as string | undefined;
      if (tool !== "ratelimit_status") return;
      const provider = (input?.args?.provider ?? output?.args?.provider) as string | undefined;
      const rows: unknown[] = [];
      for (const [p, s] of states.entries()) {
        if (provider && p !== provider) continue;
        rows.push({
          provider: p,
          rpm_tokens: Math.round(s.rpm),
          tpm_tokens: Math.round(s.tpm),
          breaker: isOpen(p) ? "open" : s.openedUntil ? "half-open" : "closed",
          recent_window: s.window,
          recent_failures: s.window.filter((x) => x === "fail").length,
        });
      }
      output.result = JSON.stringify(rows.length ? rows : { note: "no providers seen yet" }, null, 2);
    },
  } as any;
}) satisfies Plugin;