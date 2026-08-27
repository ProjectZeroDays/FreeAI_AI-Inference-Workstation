/**
 * [COMPONENT]-bridge.js - Integration Bridge Module
 * Paste as template and modify [COMPONENT] references
 */

class COMPONENTBridge {
    constructor(options = {}) {
        this.enabled = options.enabled ?? true;
        this.color = options.color ?? '#64c8ff';
        this.intensity = options.intensity ?? 1.0;
        this.overlaySelector = options.overlaySelector ?? '#component-overlay';
        this.target = null;
        this.state = {};
        
        this.init();
    }
    
    init() {
        this.createOverlay();
        this.bindEvents();
        this.startRenderLoop();
        
        // Expose for debugging
        window.COMPONENT = this;
        console.log('[COMPONENT] Bridge initialized');
    }
    
    createOverlay() {
        this.overlay = document.querySelector(this.overlaySelector) || 
            document.createElement('div');
        
        this.overlay.id = 'component-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 999999;
            overflow: hidden;
        `;
        
        if (!this.overlay.parentNode) {
            document.body.appendChild(this.overlay);
        }
        
        // Canvas for rendering
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        `;
        
        this.overlay.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // WebGL with fallback
        try {
            this.gl = this.canvas.getContext('webgl2') || 
                     this.canvas.getContext('webgl');
        } catch (e) {
            this.use2DFallback = true;
            console.warn('[COMPONENT] Using 2D fallback');
        }
    }
    
    bindEvents() {
        let self = this;
        
        document.addEventListener('mousemove', (e) => {
            self.mousePos = { x: e.clientX, y: e.clientY };
            self.updateTarget(e.target);
        });
        
        // State change events
        window.addEventListener('component-state-change', (e) => {
            Object.assign(self.state, e.detail);
        });
    }
    
    updateTarget(element) {
        this.target = element;
    }
    
    startRenderLoop() {
        let self = this;
        this.animate = function() {
            if (self.enabled) {
                self.render();
            }
            requestAnimationFrame(self.animate);
        };
        this.animate();
    }
    
    render() {
        if (!this.canvas || !this.mousePos) return;
        
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        if (this.gl) {
            this.renderGL();
        } else {
            this.render2D();
        }
    }
    
    render2D() {
        let ctx = this.ctx;
        let time = Date.now() * 0.001;
        
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Replace with component-specific rendering
        ctx.save();
        ctx.translate(this.mousePos.x, this.mousePos.y);
        // ... component render logic
        ctx.restore();
    }
    
    renderGL() {
        // Replace with WebGL-specific rendering
        this.gl.clearColor(0, 0, 0, 0);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);
    }
    
    setState(updates) {
        Object.assign(this.state, updates);
        window.dispatchEvent(new CustomEvent('component-state-change', {
            detail: this.state
        }));
    }
    
    destroy() {
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }
    }
}

// Auto-initialize
if (typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.component = new COMPONENTBridge();
        });
    } else {
        window.component = new COMPONENTBridge();
    }
}

module.exports = COMPONENTBridge;