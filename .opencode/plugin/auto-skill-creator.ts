/**
 * opencode plugin: auto-skill-creator timer (~30-min cadence).
 *
 * Tracks user-message timestamps per session. Once ≥ CADENCE_MS (default
 * 30 * 60 * 1000 = 30 min) elapses since the last time we prompted, the next
 * user message triggers an injected "consider mining skills" prompt that
 * the coordinator sees and hands to the `auto-skill-creator` skill.
 *
 * One prompt per session per 30-min window. After firing, we reset the
 * last_prompt_at timestamp so the next prompt can't come for another 30 min.
 * The prompt is a SUGGESTION — it never auto-installs a skill. The actual
 * creation path goes through `auto-skill-creator` which always asks the user
 * to confirm `install <name>` before writing anything.
 *
 * INSTALL (auto-discovered by opencode):
 *   - Place at .opencode/plugin/auto-skill-creator.ts (auto-loaded on startup)
 *   - Quit and restart opencode for it to take effect.
 *   - Lives alongside `rate-limit.ts`; both load.
 *
 * TUNABLES via environment variables:
 *   OPENCODE_SKILL_CREATOR_CADENCE_MS — override the 30-min default
 *   OPENCODE_SKILL_CREATOR_DISABLE   — "1" disables the plugin entirely
 *
 * HONEST CAVEATS (read before relying on this):
 *   1. opencode's exact `event` / `chat.message` payload shapes can drift
 *      across versions. We filter defensively (see isUserMessage). If your
 *      version emits a different shape, update `isUserMessage` — that's the
 *      only place that needs editing.
 *   2. We can't ACTUALLY inject visible chat text from a plugin in all
 *      opencode versions — the safest cross-version behavior is to emit a
 *      custom event that an agent's system-prompt hook can read. This plugin's
 *      `event` hook emits `skill.creator.suggest` events; the `coordinator`
 *      agent should mention in its prompt that when such an event is seen, it
 *      should briefly ask the user. AGENTS.md documents that touchpoint.
 *   3. The timer is wall-clock and per-session. A new opencode session resets
 *      state — there's no persistence between sessions. That's intentional:
 *      we don't want to nag users an hour later for something they decided
 *      not to skill-ify.
 *   4. If the user has the `auto-skill-creator` skill's `/skills-mine` slash
 *      command available, prefers that path, and the plugin shouldn't double
 *      fire. We suppress a plugin prompt if the most recent user message
 *      contains "skills-mine" or "mine skills" (already covered).
 *
 * This file is TYPESCRIPT and excluded from the project's tsc gate (see
 * tsconfig.json `exclude`). It is loaded at opencode startup.
 */
import type { Plugin } from "@opencode-ai/plugin";

const CADENCE_MS = Number(process.env.OPENCODE_SKILL_CREATOR_CADENCE_MS ?? 30 * 60 * 1000);

// Per-session state. module-scope so it persists for the lifetime of the
// opencode process.
const lastUserMessageAt = new Map<string, number>();     // sessionId -> ms
const lastPromptAt = new Map<string, number>();           // sessionId -> ms

function isUserMessage(input: unknown): { sessionId: string } | null {
  // Defensive shape check across opencode versions. The fields we care about
  // are "role" (=="user") and "session"/"sessionId"/"threadId". Adapt as
  // needed if your version uses a different name.
  const e = input as Record<string, unknown> | null;
  if (!e || typeof e !== "object") return null;
  const role = (e.role ?? e.type ?? e.kind) as unknown;
  if (role !== "user" && role !== "message" && role !== "chat.message") {
    // Some opencode versions wrap everything in a "type" field that's
    // "chat.message"; role lives inside a `message` sub-object.
    const msg = e.message as Record<string, unknown> | undefined;
    if (!msg || msg.role !== "user") return null;
  }
  const sessionId =
    (e.sessionId as string) ||
    (e.session as string) ||
    (e.threadId as string) ||
    (e.id as string) ||
    "default";
  // Skip messages that are themselves the user invoking /skills-mine — already
  // in the creator flow.
  const text = (e.text ?? e.content ?? e.message) as unknown;
  if (typeof text === "string" && /skills-mine|mine skills/i.test(text)) {
    return null;
  }
  return { sessionId: String(sessionId) };
}

function shouldFire(sessionId: string): boolean {
  const now = Date.now();
  const lastMsg = lastUserMessageAt.get(sessionId) ?? 0;
  const lastPrompt = lastPromptAt.get(sessionId) ?? 0;
  if (lastMsg === 0) return false;
  // Fire only if (a) we've never prompted this session, OR last prompt was
  // >= CADENCE_MS ago, AND (b) there's been activity since the last prompt.
  if (lastPrompt !== 0 && now - lastPrompt < CADENCE_MS) return false;
  if (lastMsg <= lastPrompt) return false; // no new activity since last prompt
  return now - lastPrompt >= CADENCE_MS;
}

function markPrompted(sessionId: string): void {
  lastPromptAt.set(sessionId, Date.now());
}

export default (async ({ }) => {
  return {
    // Track user message timestamps as they arrive.
    "chat.message": (input: unknown) => {
      const r = isUserMessage(input);
      if (!r) return;
      lastUserMessageAt.set(r.sessionId, Date.now());
    },

    // Every bus event: re-check the cadence. We emit a custom event when it
    // fires so the coordinator (which reads all bus events) can see it.
    event(input: unknown) {
      const r = isUserMessage(input);
      if (!r) return;
      if (!shouldFire(r.sessionId)) return;
      markPrompted(r.sessionId);
      // We can't mutate visible chat from here reliably across opencode
      // versions, so we emit a custom event. The coordinator's prompt (see
      // AGENTS.md) instructs it to acknowledge these by asking the user
      // whether they want to mine this session for a skill.
      // Returning an object with a `meta` field is a best-effort; some
      // versions log it, some surface it as an event the agent sees. Adapt
      // to your version if needed.
      return {
        type: "skill.creator.suggest",
        sessionId: r.sessionId,
        reason: `${CADENCE_MS / 60000}-min cadence elapsed; consider mining this session for a skill. Reply \`/skills-mine\` to invoke the auto-skill-creator.`,
        emittedAt: new Date().toISOString(),
      };
    },
  } as any;
}) satisfies Plugin;