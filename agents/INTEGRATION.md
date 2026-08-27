# AI Development Environment — Integration Summary

This directory contains custom-built integration modules that bring the capabilities of **opencodex**, **Agent Zero**, **oh-my-opencode-slim**, and **awesome-opencode** into FreeAI — without forking any external projects.

## Modules

| File | Purpose |
|------|---------|
| `llm_proxy.py` | Unified LLM proxy with 40+ provider routing (opencodex-style) |
| `agent_zero_memory.py` | Persistent memory system with session history and global knowledge (Agent Zero-style) |
| `specialized_agents.py` | 7 specialized agents: orchestrator, explorer, oracle, council, librarian, designer, fixer |
| `plugin_registry.py` | Plugin registry + skill loader (awesome-opencode style) |
| `agent_bridge.py` | Central hub connecting all components with intelligent routing |

## Configuration

- **LLM Proxy**: `config/llm-proxy.json` — providers, routing, caching
- **Memory Store**: `config/memory/` — session journals and global knowledge
- **Plugin Registry**: `registry/plugins.json` — discovered plugins
- **Skills**: `skills/` — loaded from agent-toolkit structure

## API Endpoints

Added to `agents/api.py`:

| Endpoint | Description |
|----------|-------------|
| `GET /env/status` | System health check |
| `POST /env/chat` | Unified chat (auto-routes to best agent) |
| `GET /env/agents` | List all specialized agents |
| `GET /env/plugins` | List plugins from registry |
| `POST /env/plugins/{name}/install` | Install a plugin |
| `GET /env/skills` | Search/list skills |
| `GET /env/memory/{session_id}` | Recall session memory |
| `POST /env/memory/search` | Search global knowledge |

## CLI

```bash
# Check system status
python ai-env status

# Chat with auto-routing
python ai-env chat "Implement a REST API"

# Chat with specific agent
python ai-env chat "Review this code" --agent oracle

# List agents
python ai-env agents

# Search skills
python ai-env skills search "testing"

# Memory operations
python ai-env memory stats
python ai-env memory recall <session_id>
python ai-env memory search "python async patterns"
```

## Usage

```python
from agents.agent_bridge import get_bridge

bridge = get_bridge()

# Auto-route a request
result = bridge.execute_with_agent("Build a todo API", session_id="my-session")

# Get memory context for a session
context = bridge.get_context("my-session")

# Find relevant skills
skills = bridge.find_skills("unit testing patterns")

# Stats
print(bridge.stats())
```
