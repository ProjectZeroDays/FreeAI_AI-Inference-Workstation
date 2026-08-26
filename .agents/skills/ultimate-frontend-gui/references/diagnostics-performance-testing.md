# Diagnostics, Performance, And Testing

Use this reference when fixing GUI bugs, performance issues, or tests.

## Frontend Diagnostics

Reproduce before patching. Gather evidence from:

- browser console exceptions
- failed network requests
- route fallback behavior
- DOM and root mount state
- hydration warnings
- layout overflow and z-index
- screenshots across viewport sizes

Common failure classes:

- blank screen
- JavaScript runtime crash
- resource path, CORS, CSP, or mixed-content failure
- React/Vue hydration mismatch
- browser extension popup failure
- CSS overflow, stacking, or flex/grid bug

The harvested `frontend-doctor` CLI lives in `scripts/frontend-doctor/`. It can be run from that directory with Node when its package metadata supports the current environment.

## Performance

Measure first:

- Lighthouse or PageSpeed for LCP, FCP, CLS, and accessibility checks
- browser Performance traces for long tasks and runtime jank
- bundle analyzer output for large dependencies
- network waterfall for render-blocking resources and image weight

Optimization order:

1. Fix correctness and broken resources.
2. Reduce render-blocking CSS/JS.
3. Optimize images with dimensions, proper formats, and lazy loading where safe.
4. Split code by route or interaction.
5. Reduce long tasks and unnecessary re-renders.
6. Virtualize large lists.
7. Re-measure the same scenario.

## Testing

Choose the layer by risk:

- Unit: pure functions, utilities, hooks
- Component: visible rendering, labels, roles, interactions
- Integration: routes, API mocks, multi-component flows
- E2E: critical user journeys and deployment-sensitive flows

Rules:

- Test user-visible behavior, not implementation detail.
- Prefer role/name selectors.
- Use `waitFor` or framework wait utilities instead of fixed sleeps.
- Mock external services with MSW or the project standard.
- Add focused tests for regressions you just fixed.

## Browser Verification

For substantial UI changes:

- run the app normally
- inspect desktop and mobile viewports
- capture screenshots if tools are available
- verify text containment, focus, primary interactions, and loaded assets
- verify canvas or 3D output is nonblank when applicable

## References

- `references/harvested/frontend-doctor.md`
- `references/harvested/frontend-performance.md`
- `references/harvested/frontend-testing.md`
- `references/harvested/ui-skills.md`
- `references/harvested/ux-architect.md`
