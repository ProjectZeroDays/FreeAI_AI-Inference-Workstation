# Harvested: motion

Source: `/root/.codex/skills/motion`

---
name: motion
description: Complete Motion.dev guidance for modern animation in React, JavaScript, and Vue, including transitions, gestures, scroll animation, springs, keyframes, and former Framer Motion patterns.
metadata:
  source_dir: lb-motion-skill-0.1.0
  version: "1.0.0"
  author: Leonardo Balland
  tags:
    - motion
    - animation
    - react
    - javascript
    - vue
    - framer-motion
    - transitions
    - gestures
    - scroll
    - spring
    - keyframes
---

# Motion.dev Documentation

Motion is a modern animation library for React, JavaScript, and Vue. It's the evolution of Framer Motion, offering:

- **Tiny size**: Just 2.3kb for the mini HTML/SVG version
- **High performance**: Hardware-accelerated animations
- **Flexible**: Animate HTML, SVG, WebGL, and JavaScript objects
- **Easy to use**: Intuitive API with smart defaults
- **Spring physics**: Natural, kinetic animations
- **Scroll animations**: Link values to scroll position
- **Gestures**: Drag, hover, tap, and more

## Quick Reference

### Installation

```bash
npm install motion
```

### Basic Animation

```javascript
import { animate } from "motion"

// Animate elements
animate(".box", { rotate: 360, scale: 1.2 })

// Spring animation
animate(element, { x: 100 }, { type: "spring", stiffness: 300 })

// Stagger multiple elements
animate("li", { opacity: 1 }, { delay: stagger(0.1) })
```

### React

```jsx
import { motion } from "motion/react"

<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 2 }}
/>
```

### Scroll Animations

```javascript
import { scroll } from "motion"

scroll(animate(".box", { scale: [1, 2, 1] }))
```

## Documentation Structure

- `quick-start.md` - Installation and first animation
- More docs to be added...

## When to Use This Skill

Use this skill when:
- Implementing animations in web applications
- Optimizing animation performance
- Creating scroll-based effects
- Building interactive UI with gestures
- Migrating from Framer Motion to Motion

## External Resources

- Official site: https://motion.dev
- GitHub: https://github.com/motiondivision/motion
- Examples: https://motion.dev/examples
