# Live Visual Control

Use this reference when a GUI needs to be seen, clicked, typed into, dragged, screen-captured, or verified live. It harvests the useful GUI parts of `desktop-control` and the existing browser verification workflow.

## Tool Choice

| Need | Preferred path |
| --- | --- |
| Web app DOM, routes, console, network, screenshots | Browser automation or Playwright |
| Native window, OS dialogs, Electron shell, app switching | Desktop control |
| Pixel color, screen region, image matching | Desktop control screenshots and OpenCV helpers |
| Form/input smoke tests | Browser automation first; desktop control for native or focus-sensitive flows |
| Visual regression or layout proof | Screenshots at desktop and mobile sizes |

## Observe-Act-Verify Loop

1. Capture the current state: screenshot, console, DOM, window title, mouse position, or pixel sample.
2. Identify the smallest next action: click, hotkey, text entry, scroll, drag, route navigation, or viewport change.
3. Execute the action with a bounded tool call.
4. Capture the result immediately after.
5. Compare expected vs actual state.
6. Continue only if the result matches the plan; otherwise diagnose from the new evidence.

This loop is mandatory for high-stakes GUI fixes, native app flows, Electron windows, complex canvas/WebGL UIs, or any case where static code inspection cannot prove the experience.

## Desktop Control Safety

- Enable failsafe when using desktop automation.
- Prefer hotkeys over fragile coordinate menus when a reliable shortcut exists.
- Use screenshots before and after action sequences.
- Use explicit pauses only for UI settling; prefer condition checks when available.
- Keep coordinates scoped to known window bounds.
- Do not run long blind action chains. Re-observe frequently.

## Useful Scripted Capabilities

The harvested desktop-control scripts and guides live under `scripts/desktop-control/`.

- `QUICK_REFERENCE.md`: mouse, keyboard, screenshots, windows, clipboard, dependencies
- `AI_AGENT_GUIDE.md`: observe-plan-act-verify desktop agent workflow
- `ai_agent.py`: task planning and screenshot-before/after execution loop
- `demo.py`: feature demo and smoke test

## Verification Targets

For a serious GUI, verify:

- window opens and focuses correctly
- primary workflow can be operated with mouse and keyboard
- screenshots show visible, non-overlapping UI
- focus is where the next action expects it
- popups, menus, drag/drop, scroll, and dialogs behave correctly
- after-action screenshot or DOM state proves the change landed

## References

- `scripts/desktop-control/QUICK_REFERENCE.md`
- `scripts/desktop-control/AI_AGENT_GUIDE.md`
- `references/advanced-harvested/desktop-control.md`
- `references/diagnostics-performance-testing.md`
