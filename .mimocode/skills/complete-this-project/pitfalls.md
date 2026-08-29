# Common Pitfalls

## Auditing Without a Plan
Don't just find problems — prioritize them. Use P0/P1/P2 severity levels.

## Dispatching Too Many Agents
More agents ≠ faster completion. Coordinate overhead grows exponentially.
- **Optimal:** 4-6 concurrent agents
- **Maximum:** 8 agents per wave
- **Beyond 8:** Batch into multiple waves

## Ignoring Test Isolation
Agents writing to shared state (databases, config files) can break other agents.
- Use in-memory databases for tests
- Isolate temp files per agent
- Clean up agent artifacts after completion

## Skipping the Audit Phase
Jumping straight to implementation without understanding the full scope leads to:
- Missing dashboards discovered late
- Inconsistent UI patterns
- Duplicate work across agents

## No Quality Gates Between Waves
Each wave must pass verification before the next starts.
- Wave 1 must pass tests before Wave 2 dispatch
- UI consistency check before documentation
- Security scan before deployment

## Forgetting Git Hygiene
Parallel agents working on the same files causes merge conflicts.
- Assign non-overlapping file paths per agent
- Use separate branches for each wave if needed
- Merge and resolve conflicts between waves

## Incomplete Handoff Messages
Agents must report exactly what they changed and how to verify.
**Bad handoff:** "Done with the dashboard."
**Good handoff:** "Created dashboard/templates/analytics.html with 3 charts (line, bar, pie), 6 data cards, date range picker. Verified against existing CSS variables. Run `python -m pytest tests/test_analytics.py -v` to test."

## Missing CI Integration
Implementation without CI verification risks breaking the build.
- Always run `python -m pytest tests/ -q` after each wave
- Check `git status` for unexpected changes
- Verify `python -c "from dashboard import backend"` imports cleanly
