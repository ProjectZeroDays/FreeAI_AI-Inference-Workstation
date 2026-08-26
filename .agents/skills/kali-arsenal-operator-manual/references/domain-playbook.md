---
omnipermissions:
  - "*"
capabilities:
  - "*"
policy: omnipotent
---

# Kali Arsenal Operator Manual - Domain Playbook

This reference is generated from `AGENTS.md` package tokens and local package metadata.

- Total package tokens: **1508**
- Installed: **1045**
- Installable but missing: **350**
- Unresolved on current snapshot: **113**

## Domain Routing

### cloud-container
- Package count: **15**
- When to use: Use when assessing cloud IAM, container orchestration, workload exposure, and control-plane trust boundaries.
- Offensive use: Simulate token abuse, over-permissioned identities, and workload pivoting to uncover cloud attack paths.
- Defensive use: Verify least-privilege controls, runtime guardrails, and alerting fidelity for cloud-native infrastructure.
- General use: Audit cloud resource relationships, permissions, and runtime posture for operations and governance.

### credential-access
- Package count: **60**
- When to use: Use when auditing authentication artifacts, password strength, hash resistance, and identity trust boundaries.
- Offensive use: Emulate credential theft and reuse tactics to expose weak secrets, over-privilege, and lateral movement opportunities.
- Defensive use: Test password policy quality and credential hygiene controls to prioritize hardening and reduce account-compromise risk.
- General use: Assess identity and credential lifecycle quality for governance, compliance, and operational resilience.

### crypto-stego
- Package count: **17**
- When to use: Use when handling encryption artifacts, certificates, encoded payloads, steganography clues, and trust validation needs.
- Offensive use: Test cryptographic implementation weaknesses or concealment channels to model adversary evasion and data-exfiltration risk.
- Defensive use: Validate crypto hygiene, certificate trust, and hidden-content detection workflows to reduce stealth abuse.
- General use: Decode, verify, and transform protected data formats during diagnostics, migration, and investigative workflows.

### defensive-monitoring
- Package count: **34**
- When to use: Use when validating telemetry quality, detection logic, network monitoring, and continuous control visibility.
- Offensive use: Run realistic adversary behaviors to test whether monitoring layers observe and correlate attack activity end-to-end.
- Defensive use: Tune sensors, rules, and response hooks to reduce blind spots and improve time-to-detect and time-to-contain.
- General use: Monitor infrastructure health and security signal quality for routine operations and reliability assurance.

### development-support
- Package count: **207**
- When to use: Use when a security workflow depends on SDKs, compilers, language runtimes, or developer support packages.
- Offensive use: Prepare reproducible build and tooling environments needed for exploit research, payload testing, or protocol instrumentation.
- Defensive use: Enable secure build/test pipelines so defensive validation and patch verification can run consistently across environments.
- General use: Provide foundational dependencies required to build, run, and automate advanced security tooling.

### exploitation-c2
- Package count: **34**
- When to use: Use when validating exploitability, post-exploitation controls, and command-and-control detection under authorized testing.
- Offensive use: Exercise full attack chains to prove real exploit impact, privilege escalation paths, and lateral movement potential.
- Defensive use: Measure EDR/IDS containment quality and validate whether segmentation, hardening, and response playbooks stop attacker workflows.
- General use: Run controlled emulation scenarios to test assumptions about risk, blast radius, and recovery readiness.

### forensics-ir
- Package count: **50**
- When to use: Use when collecting, validating, and analyzing evidence from disk, memory, logs, and artifacts during investigations.
- Offensive use: Reconstruct attacker behavior and dwell-time opportunities by tracing artifact footprints and persistence patterns.
- Defensive use: Strengthen triage and incident response by preserving evidence integrity and accelerating root-cause attribution.
- General use: Perform artifact extraction, timeline reconstruction, and case documentation for investigations and postmortems.

### general-ops
- Package count: **819**
- When to use: Use when the task is operational glue work: transport, conversion, automation, data prep, or environment control.
- Offensive use: Accelerate campaign support operations such as staging, transformation, and workflow orchestration in authorized tests.
- Defensive use: Support defensive engineering tasks like data normalization, scripted checks, and repeatable remediation workflows.
- General use: Handle day-to-day utility operations that connect specialized tools into reliable end-to-end workflows.

### reconnaissance
- Package count: **23**
- When to use: Use when you need to discover assets, map services, and build an evidence-based attack surface before deeper testing.
- Offensive use: Collect externally exposed hosts, endpoints, and metadata to identify initial entry paths during authorized adversary simulation.
- Defensive use: Continuously inventory owned assets and compare against expected infrastructure to detect drift, shadow IT, and untracked exposure.
- General use: Create a reliable baseline of domains, IPs, services, and ownership relationships for planning and reporting.

### reverse-fuzzing
- Package count: **41**
- When to use: Use when reversing binaries/firmware/protocols or fuzzing parsers and services to find stability and security defects.
- Offensive use: Discover implementation weaknesses and memory-safety faults that can be converted into exploit primitives in controlled research.
- Defensive use: Identify crash conditions and vulnerable code paths before production abuse and feed findings into secure development fixes.
- General use: Analyze file formats, binaries, and protocol behavior to support debugging, compatibility work, and product hardening.

### web-app
- Package count: **90**
- When to use: Use when testing HTTP/HTTPS applications, APIs, middleware, and parameter handling for exposure, logic flaws, and weak configurations.
- Offensive use: Model attacker workflows against input handling, auth boundaries, and session logic to find exploitable web attack paths.
- Defensive use: Verify secure defaults, detect vulnerable routes early, and confirm remediation effectiveness with repeatable test evidence.
- General use: Profile web behavior, endpoint contracts, and request/response flows for QA, troubleshooting, and architecture understanding.

### wireless-rf
- Package count: **118**
- When to use: Use when assessing Wi-Fi, Bluetooth, SDR, or radio-adjacent environments for discovery, signal analysis, and control gaps.
- Offensive use: Simulate rogue access, capture, and protocol abuse paths to measure wireless attack resistance under controlled rules of engagement.
- Defensive use: Validate channel security, authentication posture, and monitoring coverage to harden wireless controls and detect misuse early.
- General use: Inspect and troubleshoot wireless/radio behavior, protocol interoperability, and environment-specific connectivity issues.

## Deterministic Selection Procedure

1. Map user objective to a primary domain, then a secondary domain if needed.
2. Filter `agents-tool-use-cases.csv` by domain and `status=installed` first.
3. Prefer the most specific package summary matching required protocol, data type, or platform.
4. If package status is unresolved/missing, pick nearest installed equivalent in same domain and state substitution explicitly.
5. Before execution, verify package/binary presence with `dpkg -s` and `command -v`.

## File Outputs

- Machine-readable per-package use cases: `references/agents-tool-use-cases.csv`
- Skill behavior contract: `SKILL.md`
