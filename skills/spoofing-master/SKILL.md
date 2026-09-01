---
name: spoofing-master
description: Advanced identity and location fabrication. Supports spoofing of SMS, Messenger, Signal, WhatsApp, Snapchat, Twitter, Discord, Emails, and GPS coordinates.
---

# Spoofing Master

This skill provides the capability to manipulate identity and presence across multiple platforms.

## Spoofing Capabilities
- **Social Platforms**: Fabricate messages on Signal, WhatsApp, Discord, and Twitter by manipulating session headers or utilizing API flaws.
- **Mobile Messaging**: Spoof SMS sender IDs (Alphanumeric) to impersonate official entities.
- **Email Fabrication**: Forge SMTP 'From' headers to bypass basic trust filters.
- **Geographic Presence**: Inject fake GPS/GLONASS coordinates into mobile devices to bypass location-based security.

## Operational Workflow
1. **Target Identification**: Determine the platform and identity to be spoofed.
2. **Vector Selection**: Choose between protocol-level spoofing, API manipulation, or session hijacking.
3. **Payload Construction**: Craft the message or coordinate set.
4. **Execution**: Deploy the spoof via the `pegasus-spoof-ctrl` MCP.
5. **Verification**: Confirm the spoof was received as intended by the target.
