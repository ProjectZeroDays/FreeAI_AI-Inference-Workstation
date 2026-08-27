/**
 * FreeAI Teaming Plugin — registers red/blue/purple + SDLC apex agents
 * and their MCP tools with opencode.
 * Loaded via opencode.json plugins: ["./plugins/freeai-teaming"]
 */
export default async function({ client }) {
  // Agents are already declared as markdown files in .opencode/agents/
  // This plugin hooks lifecycle events for autonomous teaming.
  client.on("session.created", async ({ session }) => {
    // Inject teaming context for red/blue/purple sessions
  });
  client.on("tool.execute.before", async ({ tool, args }) => {
    // Enforce uncensored routing for red team
    if (tool === "skill" && args?.skill?.includes("red-team")) {
      // ensure router hint is set via env
      process.env.FREEAI_AGENT_HINT = "red";
    }
  });
  return {
    name: "freeai-teaming",
    version: "1.0.0",
    agents: ["red-team", "blue-team", "purple-team", "sdlc-apex"],
    skills: ["red-team-apex", "blue-team-apex", "purple-team-apex", "sdlc-apex"],
  };
}
