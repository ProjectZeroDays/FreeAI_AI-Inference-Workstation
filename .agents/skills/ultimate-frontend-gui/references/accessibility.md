# Accessibility

Use this reference for GUI implementation, audits, and bug fixes.

## Baseline

- Prefer semantic HTML before ARIA.
- Use buttons for actions and links for navigation.
- Keep visible focus states. Never remove outlines without replacing them.
- Ensure all interactive controls are keyboard reachable.
- Provide `aria-label` or visible text for icon-only controls.
- Associate labels with form controls.
- Put validation feedback near the input or action.
- Use status/live regions for async changes only when users need to be informed.
- Respect `prefers-reduced-motion`.

## Contrast

- Normal text should meet WCAG 2.1 AA contrast.
- Focus indicators should be visible against surrounding colors.
- Disabled states must still communicate affordance and state.
- Error colors need more than color alone: add text, icon, or pattern.

## Focus Management

- Modal open: move focus into the modal.
- Modal close: return focus to the triggering control.
- Drawer/popover/menu: use proper keyboard navigation and escape behavior.
- Route/view changes: move focus to the new page heading or logical first control when needed.

## Testing

Use a mix of:

- keyboard-only navigation
- screen reader semantics via roles and labels
- automated checks such as axe if available
- Playwright locators by role/name
- contrast checks for custom palettes

## References

- `references/harvested/accessibility.md`
- `references/source-references/frontend-design-agency/accessibility-checklist.md`
- `references/source-references/frontend-design-agency/focus-states-template.md`
- `references/source-references/epic-design/accessibility.md`
