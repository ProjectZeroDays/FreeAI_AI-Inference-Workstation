---
name: chatbot-manager
description: Orchestrates the interaction between the user and the framework via the GUI chatbot. Handles command parsing, framework troubleshooting, and direct system control.
---

# Chatbot Manager

This skill is the primary interface for human-AI collaboration.

## Capabilities
- **Direct Command Execution**: Translate natural language requests (e.g., "Harden the Windows node") into MCP tool calls.
- **Framework Troubleshooting**: Analyze logs and system state to fix framework errors autonomously.
- **Contextual Q&A**: Answer user questions about the framework's state, target intel, or operational progress.
- **Process Management**: Start, stop, and monitor background tasks (e.g., "Stop the reconnaissance on Target B").

## Interaction Loop
1. **Intent Recognition**: Parse the user's message to identify the requested action.
2. **Tool Mapping**: Map the intent to a specific MCP server tool.
3. **Execution & Feedback**: Execute the tool and report the result in a human-readable format.
