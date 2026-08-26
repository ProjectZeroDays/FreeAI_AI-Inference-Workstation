---
name: quantum-gui-builder
description: Builds new pages for the Quantum AEGIS-Q tkinter GUI. Follows the established pattern from aegis_theme.py and aegis_main_window.py. Use when adding a new page to the Python GUI, creating custom panels, or extending the tkinter interface.
---

# Quantum GUI Builder

Creates new tkinter pages following the AEGIS-Q theme conventions.

## Architecture

- **Theme**: `core/gui/aegis_theme.py` — AEGISTheme class with c2.html exact colors
- **Main Window**: `core/gui/aegis_main_window.py` — 18-page notebook layout
- **Combined Entry**: `core/gui/aegis_combined.py` — Combined GUI launcher

## Theme Constants (from AEGISTheme)

```python
BG = "#02040a"          # --bg
PANEL = "#030e1e"       # --panel
ACCENT = "#00e5ff"      # --accent
DANGER = "#ff4b6b"      # --danger
MUTED = "#7fa2b8"       # --muted
SUCCESS = "#6ef0a3"     # --success
WARN = "#ffd36b"        # --warn
GLASS = "#002833"       # --glass (approx)
BORDER = "#103347"      # --border (approx)
LIGHT = "#cfefff"       # --light
FONT = "Segoe UI"       # --font
MONO = "Consolas"       # --mono (tkinter equivalent)
```

## tkinter Limitations

- **NO 8-char hex**: `#RRGGBBAA` is invalid. Use `#RRGGBB` only.
- **NO `-command` on Label**: Use `Label.bind("<Button-1>", cb)` or `tk.Button`.
- **NO CSS variables**: Hardcode color values from AEGISTheme constants.
- **NO letter_spacing**: Not a valid tkinter option. Remove it.

## Page Template

```python
def _create_my_page(self):
    """Create My Page panel."""
    page = tk.Frame(self.notebook, bg=AEGISTheme.BG)
    self.notebook.add(page, text=" My Page ")

    # Header
    header = tk.Frame(page, bg=AEGISTheme.BG)
    header.pack(fill=tk.X, padx=15, pady=(15, 5))
    tk.Label(header, text="MY PAGE",
             bg=AEGISTheme.BG, fg=AEGISTheme.ACCENT,
             font=(AEGISTheme.FONT, 14, "bold")).pack(side=tk.LEFT)

    # Content area
    content = tk.Frame(page, bg=AEGISTheme.BG)
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    # Panel card
    card = tk.Frame(content, bg=AEGISTheme.PANEL,
                    highlightbackground=AEGISTheme.BORDER,
                    highlightthickness=1)
    card.pack(fill=tk.BOTH, expand=True, pady=5)

    # Add widgets inside card...
    tk.Label(card, text="Content here",
             bg=AEGISTheme.PANEL, fg=AEGISTheme.LIGHT,
             font=(AEGISTheme.FONT, 11)).pack(padx=10, pady=10)

    return page
```

## Adding to Main Window

1. Create the `_create_my_page()` method
2. Call it in `__init__` after other pages
3. Add the page frame to `self.pages` dict: `self.pages["my_page"] = self._create_my_page()`

## Widget Styling Rules

- All Frames: `bg=AEGISTheme.BG`
- All Labels: `bg=AEGISTheme.BG` or `bg=AEGISTheme.PANEL`, `fg=AEGISTheme.LIGHT`
- Accent text: `fg=AEGISTheme.ACCENT`
- Buttons: `bg=AEGISTheme.GLASS`, `fg=AEGISTheme.ACCENT`, `relief="flat"`
- Active buttons: `activebackground=AEGISTheme.ACCENT`, `activeforeground=AEGISTheme.BG`
- Scrollable content: Use `tk.Canvas` + `tk.Scrollbar` pattern
- Tables/lists: `ttk.Treeview` with dark theme settings
