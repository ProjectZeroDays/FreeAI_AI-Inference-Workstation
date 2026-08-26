---
name: tdd-restoration
description: Guide for restoring missing framework components using a strict Test-Driven Development (TDD) loop. Use when rebuilding legacy or missing codebase components to ensure each part is verified before proceeding.
---

# TDD-Driven Restoration

This skill implements a strict TDD loop for restoring missing or broken components of a framework. It prevents "blind implementation" and ensures that every piece of restored code serves a verified purpose.

## The Restoration Loop

For every component or feature being restored, follow these steps in exact order:

1. **Identify the Component**: Define the specific class, function, or module that needs restoration.
2. **Design a Failing Test**:
   - Create a unit test that targets the missing functionality.
   - The test MUST fail (or be unrunnable/import-error) because the component is missing or incomplete.
   - Document the expected behavior in the test case.
3. **Minimal Implementation**:
   - Write the absolute minimum amount of code required to make the test pass.
   - Avoid adding "future-proof" logic, extra features, or unnecessary abstractions.
   - Focus only on the interface and basic logic required by the test.
4. **Verify and Pass**:
   - Run the test.
   - If it fails, refine the implementation.
   - Once it passes, the component is considered "baselined."
5. **Advance**:
   - Only after the test passes should you move to the next component or add the next specific requirement to the current one (repeating the loop).

## Guidelines for Restoration

- **Surgical Changes**: Do not refactor existing working code unless the TDD loop explicitly requires it to make a test pass.
- **Dependency Ordering**: Restore components from the bottom up (lowest level utilities first, then higher-level orchestrators).
- **Baseline First**: Get the system to a "minimally functional" state before adding optimizations.
- **Test-as-Documentation**: The resulting test suite should serve as the primary technical documentation for how the restored components are intended to work.

## Stopping Condition

The restoration of a module is complete when all defined requirements for that module are covered by passing tests and no "stub" or "simulated" code remains.
