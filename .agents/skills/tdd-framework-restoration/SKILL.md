---
name: tdd-framework-restoration
description: Implements a strict Test-Driven Development (TDD) cycle for restoring missing or stubbed codebase components. Use when restoring framework logic where correctness must be verified per-component via a Fail -> Implement -> Pass loop.
---

# TDD Framework Restoration

## Workflow
1. **Identify Target**: Define the component or function to be restored and its expected behavior.
2. **Write Failing Test**: Create a unit test that asserts the desired behavior. Run the test and verify it fails.
3. **Minimal Implementation**: Write the absolute minimum code required to make the test pass.
4. **Verify Pass**: Run the test and verify it passes.
5. **Refactor**: Clean up the implementation if necessary.
6. **Repeat**: Return to Step 2 for the next requirement of the component.

## Guidance
- **Surgical Changes**: Only modify the target component. Do not refactor adjacent code unless necessary for the test to run.
- **Small Increments**: Each test-pass cycle should be as small as possible.
- **Verification**: Always run the full test suite to ensure no regressions were introduced.
