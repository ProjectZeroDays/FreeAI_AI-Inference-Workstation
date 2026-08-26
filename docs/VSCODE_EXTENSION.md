# VSCode Extension (ROADMAP 10)

Stub: `vscode-extension/` contains a minimal extension that:
- Adds `FreeAI: Route Prompt` command (sends selection to `http://localhost:8010/route`)
- Streams response into an editor tab
- Hot reload: `npm run watch` rebuilds on save; `F5` launches Extension Development Host
- Debug: `launch.json` with `request: launch` for the extension

Install locally: `code --install-extension freeai-0.1.0.vsix` (build with `vsce package`).
