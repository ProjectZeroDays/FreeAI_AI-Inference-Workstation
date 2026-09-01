# FreeAI Examples

Collection of standalone demos and quickstarts demonstrating FreeAI patterns.

## Quickstart

```bash
# Local code assistant (requires Ollama)
python examples/local-code-assistant/assistant.py --local

# Claude/Opus adapter demo
python examples/adapter-claude-opus/claude_adapter.py --provider ollama --prompt "Explain concurrency"
python examples/adapter-claude-opus/claude_adapter.py --provider agnes --key $AGNES_API_KEY

# Jarvis agent demo (with memory + tools)
python examples/jarvis-demo/jarvis_agent.py --key $AGNES_API_KEY

# CLI chat
python examples/demos/cli_chat.py --key $AGNES_API_KEY --prompt "Hello"

# Streaming chat
python examples/demos/streaming_chat.py --key $AGNES_API_KEY

# Code completion
python examples/demos/code_completion.py --key $AGNES_API_KEY --file mycode.py
```

## Categories

### `local-code-assistant/`
Privacy-first, offline-capable code assistant using Ollama or any OpenAI-compatible API.
- Supports local Ollama models or remote providers
- Persistent config at `~/.freeai/code-assistant.json`
- REPL mode with history

### `adapter-claude-opus/`
Provider adapter patterns with unified interface:
- `AgnesAdapter` — FreeAI primary provider
- `OllamaAdapter` — local models
- `OpenAIAdapter` — OpenAI-compatible endpoints
- `ProviderRouter` — dynamic provider switching

### `jarvis-demo/`
Agent orchestration demo showing:
- `ConversationMemory` — turn-based context with summarization
- `ToolRegistry` — extensible tool system
- `JarvisAgent` — LLM + tools + memory loop

### `demos/`
Single-purpose demo apps:
- `cli_chat.py` — basic chat REPL
- `code_completion.py` — context-aware code suggestions
- `streaming_chat.py` — SSE token streaming

## Integration with FreeAI

These examples use the same patterns as the FreeAI core:
- `agents/specialized/` — agent registry
- `router/` — provider routing
- `llm_proxy.py` — multi-provider gateway

See `agents/specialized/campaign_agent.py` for production-grade agent patterns.
