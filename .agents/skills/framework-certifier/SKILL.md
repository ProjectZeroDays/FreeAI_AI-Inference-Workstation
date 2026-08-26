---
name: framework-certifier
description: Autonomous verification and certification of the framework. Performs a full-stack audit from GUI $\rightarrow$ API $\rightarrow$ MCP $\rightarrow$ Engine to ensure 100% operational readiness.
---

# Framework Certifier

This skill is the final gate before production. It ensures that no "placeholder" remains and every button works.

## The Certification Loop
1. **Discovery**: Scan `settings.json` and `plugin.json` files to list every expected feature.
2. **Connectivity Test**: 
   - Ping the API Gateway.
   - Send a test request to every MCP server.
   - Verify the Engine returns a valid response.
3. **UI Audit**: Check `App.tsx` to ensure every defined widget in `settings.json` has a corresponding React component.
4. **Smoke Testing**: Execute one basic "Happy Path" operation for every module (e.g., "Create one spoofed identity").
5. **Documentation Sync**: Verify that `Project Features.md` and `WIKI.md` match the actual implemented code.

## Certification Report
The skill generates a `CERTIFICATION_REPORT.md` containing:
- **Pass/Fail** for every module.
- **Latency metrics** for AI responses.
- **Missing link** warnings (e.g., "Button X in GUI does not call API Y").
- **Final Production Score** (%).
