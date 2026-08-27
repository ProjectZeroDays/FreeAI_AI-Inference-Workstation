# Motion System Guide

Nutze diese Anleitung für konsistente Animationen in deiner UI.

## Timing Tokens

| Token | Wert | Verwendung |
|-------|------|------------|
| `--motion-fast` | 150ms | Micro-interactions (Hover, Toggle) |
| `--motion-normal` | 300ms | Standard-Übergänge (Modal, Drawer) |
| `--motion-slow` | 500ms | Emphasis-Animationen (Page Load) |

## Easing Functions

| Name | CSS Value | Verwendung |
|------|-----------|------------|
| `ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard-Übergänge |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elemente, die aus dem Screen verschwinden |
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Elemente, die in den Screen eintreten |
| `ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Spielereiche Interactions |

## CSS-Variablen Template

```css
:root {
  /* Timing */
  --motion-fast: 150ms;
  --motion-normal: 300ms;
  --motion-slow: 500ms;

  /* Easing */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

## Motion Prinzipien

### 1. Was animiert werden SOLLTE
- **Hover States**: Buttons, Links, Cards
- **Focus States**: Inputs, Buttons, Menüs
- **Zustandswechsel**: Loading → Success, Empty → Content
- **Appear/Disappear**: Modals, Dropdowns, Toasts
- **Feedback**: Button-Press, Selection

### 2. Was STATISCH bleiben sollte
- **Primärer Content**: Text, Bilder, Daten
- **Navigation**: Header-Links (nur Unterstreichung)
- **Hintergründe**: Canvas, Surface (keine ständige Animation)
- **Daten**: Tabelleninhalte, Charts (nur Update-Animation)

### 3. Choreographie

**Staggered Reveals** (Sequenzielle Einblendung):
```css
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
```

**Page Load Priorität**:
1. Primary Action (0ms)
2. Content (100ms)
3. Secondary Elements (200ms)
4. Decorative (300ms)

## Micro-Interactions

### Button Hover
```css
.button {
  transition: transform var(--motion-fast) var(--ease-default),
              box-shadow var(--motion-fast) var(--ease-default);
}
.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.button:active {
  transform: translateY(0);
  transition-duration: var(--motion-fast);
}
```

### Card Hover
```css
.card {
  transition: transform var(--motion-normal) var(--ease-default),
              border-color var(--motion-fast) var(--ease-default);
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
}
```

### Input Focus
```css
.input {
  transition: border-color var(--motion-fast) var(--ease-default),
              box-shadow var(--motion-fast) var(--ease-default);
}
.input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.15);
}
```

### Modal/Dialog
```css
@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal {
  animation: modal-in var(--motion-normal) var(--ease-out);
}
```

### Toast/Notification
```css
@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(-100%) translateX(-50%);
  }
  to {
    opacity: 1;
    transform: translateY(0) translateX(-50%);
  }
}

@keyframes toast-out {
  to {
    opacity: 0;
    transform: translateY(-100%) translateX(-50%);
  }
}

.toast {
  animation: toast-in var(--motion-normal) var(--ease-out);
}
.toast.exiting {
  animation: toast-out var(--motion-fast) var(--ease-in) forwards;
}
```

## Reduced Motion

Respektiere Benutzerpräferenzen:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Verboten

- ❌ Konstante Pulsier-Animationen
- ❌ Automatisch ablaufende Karussells ohne Pause
- ❌ Parallax-Scrolling ohne Reduced-Motion-Fallback
- ❌ Animationen > 1s (außer Page-Load)
- ❌ Mehr als 3 gleichzeitige Animationen

## Checkliste

Vor Implementierung:
- [ ] Timing-Tokens definiert?
- [ ] Easing-Funktion ausgewählt?
- [ ] Reduced-Motion-Query berücksichtigt?
- [ ] Performance geprüft (nur transform/opacity)?
- [ ] Animation hat funktionalen Zweck?
