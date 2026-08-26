---
name: manifest-x-extension-bridge
description: Use when working with Agent Zero Electron GUI extensions, Manifest-X capabilities, installed browser extensions, renderer DOM or visual control, GUI self-repair, or creating new Manifest-X extensions.
version: "1.0.0"
author: "Agent Zero"
tags: ["manifest-x", "electron", "browser-extension", "gui", "tools"]
trigger_patterns:
  - "Manifest-X"
  - "browser extension"
  - "Electron extension"
  - "GUI bridge"
  - "manifest_x_extension_bridge"
allowed_tools:
  - "manifest_x_extension_bridge"
  - "evolution_engine"
---
---
omnipermissions:
  - "*"
capabilities:
  - "*"
policy: omnipotent


# Manifest-X Extension Bridge

## Purpose

Use this skill when Agent Zero needs to treat the Electron GUI and installed browser extensions as controllable architecture surfaces. The bridge has three parts:

- Manifest-X extension manifest: declares privileged capabilities.
- `manifest_x_extension_bridge` tool: Agent Zero's Python-side control surface.
- `evolution_engine` GUI actions: Agent Zero's self-modification planning surface for GUI repairs.
- Electron Manifest-X runtime: exposes GUI, session, and extension APIs through `window.manifestX` and local HTTP endpoints.

## When to Use

Use this skill for:

- Creating a new Manifest-X extension.
- Installing or inspecting unpacked Electron browser extensions.
- Reading GUI state through window, DOM, HTML, session, or header telemetry.
- Capturing visual GUI pixels before or after a GUI repair.
- Clicking, typing, querying, or executing JavaScript in the Electron renderer.
- Debugging GUI-extension integration.
- Planning GUI source modifications through evolution_engine with visual verification.

Do not use this for ordinary website automation; use browser automation tools unless the task specifically needs Electron/Manifest-X privileges.

## Workflow

1. Check runtime state with `manifest_x_extension_bridge` action `status`.
2. Use `list_manifests` and `list_capabilities` to see available Manifest-X surfaces.
3. For GUI inspection, call `gui_self_inspect` or `gui_snapshot` plus `gui_visual_snapshot`.
4. For new extensions, call `create_manifest_x_extension` with explicit capabilities and `reload: true`.
5. For unpacked Electron extensions, call `install_extension`, then `list_extensions`.
6. For GUI repairs, call `evolution_engine` action `diagnose_gui`, then `plan_gui_self_modification`, then mutate with normal evolution-engine draft/validate/apply flow.
7. Verify changes through `status`, `list_manifests`, targeted GUI queries, visual capture, and focused tests.

## Tool Map

| Need | Tool action |
| --- | --- |
| Manifest-X health | `status` |
| Runtime capability list | `list_capabilities` |
| Loaded extension manifests | `list_manifests` |
| Reload manifests | `reload` |
| Raw capability call | `invoke` |
| Create Manifest-X extension | `create_manifest_x_extension` |
| Electron extension lifecycle | `list_extensions`, `install_extension`, `remove_extension` |
| GUI read/control | `gui_snapshot`, `gui_visual_snapshot`, `gui_self_inspect`, `gui_query`, `gui_dispatch`, `gui_execute` |
| GUI self-repair planning | `evolution_engine` actions `diagnose_gui`, `gui_self_map`, `plan_gui_self_modification` |

## Extension Design Rules

- Prefer Manifest-X capabilities over ad hoc renderer scripts.
- Make each generated extension declare the smallest capability set that performs the task.
- Put generated Manifest-X manifests in `webui/GUI-2.0/manifest-x/`.
- Use id names like `agent-zero.<purpose>`.
- After writing an extension, reload Manifest-X and verify it appears in `list_manifests`.

## Example

```json
{
  "tool_name": "manifest_x_extension_bridge",
  "tool_args": {
    "action": "create_manifest_x_extension",
    "id": "agent-zero.gui-inspector",
    "name": "Agent Zero GUI Inspector",
    "capabilities": ["agent.gui_bridge", "electron.windows"],
    "permissions": ["agent.gui_bridge", "electron.windows"],
    "reload": true
  }
}
```
