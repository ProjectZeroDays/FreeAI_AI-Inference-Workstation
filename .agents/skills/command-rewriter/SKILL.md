---
name: command-rewriter
description: "Converts natural-language user prompts into precise shell/terminal commands. Use when the user asks to 'do X' and the task requires running commands — e.g., 'restart the backend', 'run migrations', 'install dependencies', 'check the logs', 'deploy to production'."
---

# Command Rewriter

Translates user intents into exact CLI commands with safety checks, context awareness, and error-prevention.

## When to Use

- User says something like: "restart the server", "run the tests", "deploy this", "check why it failed", "install that package"
- The prompt implies a command but doesn't specify the exact one
- Before running any command that modifies the system, ask for confirmation if it's destructive

## Process

1. **Understand intent** — What is the user actually trying to achieve?
2. **Check project context** — Read `package.json`, `requirements.txt`, `Makefile`, `docker-compose.yml`, or equivalent to find the correct commands
3. **Construct command** — Use the project's actual tooling (not guesses)
4. **Safety check** — Flag destructive operations (deletes, drops, pushes to prod) before running
5. **Execute** — Run the command and report results

## Examples

| User Prompt | Action |
|---|---|
| "restart the backend" | Read project structure, find backend entry point, run `cd backend && python main.py` or `npm run dev` |
| "run migrations" | Check for alembic, django migrate, prisma migrate, etc. and run the correct one |
| "install dependencies" | Detect package manager (npm, pnpm, pip, cargo) and run accordingly |
| "check the logs" | Find log files or run the service's log command |
| "deploy to production" | Show the deploy command and ask for confirmation before running |
| "what's wrong with the build" | Run the build command and analyze the error output |

## Rules

- Always read the project's configuration files before guessing commands
- Use `--dry-run` when available for destructive operations
- Never run `rm -rf /` or equivalent without explicit confirmation
- If multiple commands could work, pick the one that matches the project's conventions
- Report the exact command you ran and its output to the user
