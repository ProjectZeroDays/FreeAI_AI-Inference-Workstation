# UI Enhancements (ROADMAP 5)

- **Drag-and-drop designer:** `ui/dragdrop.js` (SortableJS) -- reorder workflow steps.
- **Prompt templates/history:** `ui/templates/` + localStorage `freeai-prompt-history`.
- **Theme toggle:** `ui/theme.js` -- light/dark, persisted.
- **Multi-tab UI:** dashboard tabs (Overview / Workflows / Logs / Settings) via `ui/tabs.js`.
- **Model load-time charts:** `GET /api/models/timings` ? Chart.js bar.
- **Logs viewer:** `GET /api/logs/stream` SSE tail.

All are progressive enhancements; the dashboard works without them.
