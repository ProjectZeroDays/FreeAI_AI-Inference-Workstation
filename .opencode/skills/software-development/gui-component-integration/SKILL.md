---
name: gui-component-integration
description: "Integrate interactive components into Electron/React GUIs with state hooks, IPC bridges, and fallback mechanisms"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [gui, electron, integration, ipc, react, canvas, webgl, overlay]
    related_skills: [plan, subagent-driven-development, test-driven-development]
---

# GUI Component Integration

Use this skill when integrating interactive components (canvas overlays, custom cursors, WebGL effects, drag-drop zones) into Electron/React web-based GUIs.

## Core Pattern

Every GUI component integration requires 4 files:

1. **Component Bridge** (`*-bridge.js`) - Core logic with fallback
2. **Renderer Hook** (`renderer-hook.js`) - Auto-injection script  
3. **Main Integration** (`main-integration.js`) - Electron IPC handlers
4. **State Integration** (`store-integration.ts`) - State management binding

## Standard Structure

```
project/
├── component-integration/
│   ├── component-bridge.js      # Main module
│   ├── renderer-hook.js         # Renderer injection
│   ├── main-integration.js      # Main process IPC
│   └── store-integration.ts     # State binding
├── ELASTIC-MESH-CURSOR-INTEGRATION-PLAN/
│   ├── PPP-IMPLEMENTATION-PLAN.md
│   ├── INTEGRATION-COMPLETE.md
│   ├── QUICK-START.md
│   └── elastic-mesh-integrator.js
```

## Implementation Template

### 1. Bridge Module (cursor-bridge.js)
```javascript
class ComponentBridge {
    constructor(options = {}) {
        this.enabled = options.enabled ?? true;
        this.createOverlay();
        this.bindEvents();
        this.startRenderLoop();
    }
    
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.style.cssText = `
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            pointer-events: none;
            z-index: 999999;
        `;
        document.body.appendChild(this.overlay);
    }
    
    bindEvents() {
        document.addEventListener('mousemove', (e) => {
            this.mousePos = { x: e.clientX, y: e.clientY };
        });
    }
    
    // ALWAYS include 2D fallback
    render() {
        if (this.webglContext) {
            this.renderWebGL();
        } else {
            this.render2D(); // Canvas fallback
        }
    }
}
```

### 2. Renderer Hook (renderer-hook.js)
```javascript
(function() {
    if (window.__COMPONENT_HOOK__) return;
    window.__COMPONENT_HOOK__ = true;
    
    const script = document.createElement('script');
    script.src = '../component-integration/component-bridge.js';
    document.head.appendChild(script);
})();
```

### 3. Quick-Start Pattern
Create `QUICK-START.md` with 3 deployment methods:
- Single script tag for rapid testing
- Module import for structured projects
- Automated deployment script for production

## User Preference (Learned)

When user says "skip asking questions" or "jump right into analyzing":
- Proceed immediately to implementation
- Create plan and code in parallel
- Provide execution commands at end
- No clarification loops

#### Templates

- `templates/component-bridge-template.js` - Ready-to-modify bridge module template
- `scripts/deploy-template.js` - Automated deployment script generator

#### References

- `references/elastic-mesh-cursor-session.md` - Session-specific implementation details

## Pitfalls

### Pitfall 1: No Fallback
**Problem:** WebGL-only components crash on unsupported systems
**Fix:** Always implement 2D canvas fallback inside `render()` method
**Code:** Check `this.webglContext || this.canvas2d` before render

### Pitfall 2: Missing pointer-events: none
**Problem:** Overlay blocks all UI interactions
**Fix:** Always set `pointer-events: none` on overlay container

### Pitfall 3: Z-index Conflicts
**Problem:** Component renders behind UI elements
**Fix:** Use `z-index: 999999` (not 9999) to clear floating UIs

### Pitfall 4: State Desync
**Problem:** Component doesn't react to app state changes
**Fix:** Dispatch `cursor-state-change` CustomEvent on every state change
**Code:** `window.dispatchEvent(new CustomEvent('component-state-change', {detail: this.state}));`

## Verification

```bash
# Run standalone test
npx http-server . -p 8080
open http://localhost:8080/component-integration/test-integration.html

# Run automated tests
npm test -- --testPathPattern=component

# Deploy to project
node component-integration/elastic-mesh-integrator.js
```

## Integration Checklist

- [ ] Bridge module created with fallback
- [ ] Renderer hook for auto-injection
- [ ] IPC handlers in main process
- [ ] State integration with store
- [ ] `pointer-events: none` on overlay
- [ ] `z-index: 999999` on overlay
- [ ] CustomEvent for state changes
- [ ] Standalone test file created
- [ ] Deploy script generated
- [ ] Quick-start documentation