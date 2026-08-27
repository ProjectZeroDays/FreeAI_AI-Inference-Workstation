# Coverage Map

This map records the GUI-related skills harvested into `ultimate-frontend-gui`, what was preserved, and whether the old skill can be removed from active discovery.

## Harvested And Replaceable

| Skill | Source | Preserved coverage | Replacement decision |
| --- | --- | --- | --- |
| accessibility | `/root/.codex/skills/accessibility` | WCAG 2.1 AA, semantic HTML, focus, keyboard navigation, ARIA, forms, live regions, contrast | Archive after verification |
| awwwards-design | `/root/.codex/skills/awwwards-design` | memorable web design, storytelling, creative interaction, premium motion, visual craft | Archive after verification |
| css-animations | `/root/.codex/skills/css-animations` | deterministic CSS keyframes, animation-delay seeking, fill modes, HyperFrames timing constraints | Archive after verification |
| epic-design | `/root/.codex/skills/epic-design` | cinematic 2.5D websites, scroll storytelling, parallax, layered assets, validation scripts | Archive after verification |
| frontend-design-3 | `/root/.codex/skills/frontend-design-3` | distinctive production UI, bold aesthetic direction, anti-generic rules | Archive after verification |
| frontend-design-agency | `/root/.codex/skills/frontend-design-agency` | design systems, personas, research workflow, tokens, layout, quality gates, reference templates | Archive after verification |
| frontend-design-imported | `/root/.codex/skills/frontend-design-imported` | migrated frontend-design-3 source variant | Archive after verification |
| frontend-design-pro | `/root/.codex/skills/frontend-design-pro` | audit, polish, critique, color, animation, design quality review | Archive after verification |
| frontend-doctor | `/root/.codex/skills/frontend-doctor` | white screen, JS error, resource, hydration, extension popup, and CSS layout diagnostics plus CLI scripts | Archive after verification |
| frontend-performance | `/root/.codex/skills/frontend-performance` | LCP, FCP, CLS, runtime jank, bundle analysis, measurement-first optimization | Archive after verification |
| frontend-testing | `/root/.codex/skills/frontend-testing` | unit, component, integration, E2E strategy, selectors, mocks, async test stability | Archive after verification |
| motion | `/root/.codex/skills/motion` | Motion.dev and Framer Motion successor patterns for React, JS, Vue, scroll, gestures, springs | Archive after verification |
| openclaw-flutter-animations | `/root/.codex/skills/openclaw-flutter-animations` | Flutter implicit, explicit, Hero, staggered, and physics-based animation guidance | Archive after verification |
| superdesign | `/root/.codex/skills/superdesign` | layout planning, theme patterns, animation planning, modern visual polish | Archive after verification |
| ui-skills | `/root/.codex/skills/ui-skills` | component primitive rules, Tailwind constraints, focus/ARIA, safe-area, motion and performance constraints | Archive after verification |
| ultimate-frontend | `/root/.codex/skills/ultimate-frontend` | all-in-one frontend workflow, anti-slop rules, research, taste, critique | Archive after verification |
| ux-architect | `/root/.codex/skills/ux-architect` | CSS architecture, design tokens, layout framework, component hierarchy, responsive breakpoints, theming | Archive after verification |
| web-animation-design | `/root/.codex/skills/web-animation-design` | easing, timing, springs, transition choices, motion reviews, reduced motion, performance | Archive after verification |
| frontend-design | `/root/.agents/skills/frontend-design` | distinctive production-grade frontend interfaces and non-generic visual design | Archive after verification |
| frontend-design-3 symlink | `/root/.agents/skills/frontend-design-3` | symlink to `/root/.codex/skills/frontend-design-3`; covered by harvested frontend-design-3 | Remove symlink after archive |
| superdesign symlink | `/root/.agents/skills/superdesign` | symlink to `/root/.codex/skills/superdesign`; covered by harvested superdesign | Remove symlink after archive |

## Adjacent Skills Kept Active

These were considered GUI-related but remain active because their scope is broader, non-duplicative, or useful outside frontend GUI work.

| Skill | Reason kept |
| --- | --- |
| web | General website build, debug, deploy, server, framework, SEO, and web platform reference beyond GUI consolidation |
| browser-automation | Browser driving, extraction, screenshots, forms, and inspection as a general automation tool |
| e2e-testing-patterns | Broad Playwright/Cypress suite architecture and CI guidance beyond GUI implementation |
| fullstack-developer | Full stack backend, database, API, DevOps, and architecture coverage |
| build-game | Dedicated 3D browser game generation and game-specific asset/rendering workflow |
| game-architect | Game system architecture including UI but not reducible to GUI design |
| game-developer | Unity/Unreal/game implementation coverage |
| eno | Frontend architecture and stack analysis plus OpenHarmony/monorepo coverage that remains useful as a separate analyzer |
| test-master | General test strategy across domains |
| developer | General coding and architecture baseline |

## Support Files Preserved

- Harvested full source bodies: `references/harvested/*.md`
- Advanced harvested source bodies: `references/advanced-harvested/*.md`
- Frontend Design Agency references: `references/source-references/frontend-design-agency/`
- Epic Design references: `references/source-references/epic-design/`
- UX Architect references: `references/source-references/ux-architect/`
- Motion docs: `references/source-references/motion-docs/`
- Web Animation practical tips: `references/source-references/web-animation-design/PRACTICAL-TIPS.md`
- Frontend Doctor scripts: `scripts/frontend-doctor/`
- Epic Design scripts: `scripts/epic-design/`
- Desktop Control scripts and guides: `scripts/desktop-control/`
- Build Game serve helper: `scripts/build-game/`
- Blender headless runner: `scripts/blender-animation/`

## Advanced GUI Upgrade Sources

These additional provided skills were harvested into `ultimate-frontend-gui` during the advanced upgrade.

| Skill | Source | Preserved coverage | Active-skill decision |
| --- | --- | --- | --- |
| desktop-control | `/root/Downloads/skillz/skills (2)/desktop-control` | OS-level screenshots, mouse, keyboard, window activation, clipboard, image matching, observe-plan-act-verify desktop automation | Harvested into `references/live-visual-control.md`; original active `desktop-control` kept because it is also a general automation skill |
| build-game | `/root/Downloads/skillz/skills/build-game` | Three.js render loops, camera/input patterns, HUDs, post-processing, procedural assets, game system modes, browser serve helper | Harvested into `references/game-grade-gui-systems.md` and `references/physics-3d-canvas.md`; original active `build-game` kept for full game generation |
| game-architect | `/root/Downloads/skillz/skills/game-architect` | UI module architecture, state/time systems, scene/spatial systems, algorithms, DDD/data-driven/prototype paradigms | Harvested into `references/game-grade-gui-systems.md`; original active skill kept for full game architecture |
| game-developer | `/root/Downloads/skillz/skills/game-developer` | ECS, object pooling, command pattern, game performance, Unity/Unreal implementation references | Harvested into `references/game-grade-gui-systems.md`; original active skill kept for engine-specific development |
| game-designer-toolkit | `/root/Downloads/skillz/skills/game-designer-toolkit` | system design, level design, GDD templates, progression and design documentation patterns | Harvested as advanced references for complex interaction and product/game-system planning |
| game-ai | `/root/Downloads/skillz/skills/game-ai` | FSMs, behavior trees, utility AI, GOAP, pathfinding, decision systems | Harvested as interaction-state and intelligent-behavior reference for complex GUI agents/simulations |
| game-cog | `/root/Downloads/skillz/skills (2)/game-cog` | cohesive game asset generation, UI elements, 3D models, prototypes, world/level assets | Harvested into `references/physics-3d-canvas.md`; original active skill kept for CellCog-specific generation |
| blender-animation | `/root/Downloads/skillz/skills/blender-animation` | headless Blender scene/video rendering, camera, lighting, MP4 output workflow | Harvested into `references/physics-3d-canvas.md`; migrated active skill kept because it is not only GUI |
| ai-animation-3d-model | `/root/Downloads/skillz/skills (2)/ai-animation-3d-model` | cloud 3D model animation and 1080p video export workflows | Harvested into `references/physics-3d-canvas.md`; migrated active skill kept for direct model-animation tasks |
| physics-animation-workflow | `/root/Downloads/skillz/skills/physics-animation-workflow` | coordinate systems, vectorization, physics calculation, interactive Canvas animation | Harvested into `references/physics-3d-canvas.md`; migrated active skill kept for standalone physics animation tasks |
| fullstack-developer | `/root/Downloads/skillz/skills/fullstack-developer` | production frontend/fullstack component, state, API, architecture, and testing guidance | Harvested lightly; original active skill kept because it covers backend and full-stack work |
| agent-team-orchestration | `/root/Downloads/skillz/skills (2)/agent-team-orchestration` | task lifecycle, handoffs, review loops for large GUI builds | Harvested as coordination reference; active orchestration skill kept |
