# Campaign Landing Pages

Phishing simulation landing pages for red team campaigns.

## Pages

| File | Description | Brand |
|------|-------------|-------|
| `microsoft_login.html` | Microsoft 365 sign-in page | Microsoft |
| `google_workspace.html` | Google Workspace sign-in page | Google |
| `adobe_sign.html` | Adobe Sign document signature page | Adobe |

## Tracking Parameters

All pages accept URL query parameters for campaign tracking:

```
?campaign=CAMP-20260831-001&variant=V1&user=user123
```

- `campaign` - Campaign ID (required for analysis)
- `variant` - Variant identifier (V1, V2, V3)
- `user` - User identifier
- `timestamp` - ISO timestamp
- `id` - Unique visit ID

## Usage

### Test Mode (Recommended)
```powershell
python scripts/landing_server.py --port 8080 --page microsoft_login.html --campaign CAMP-TEST --variant V1
```

Then open: `http://127.0.0.1:8080/microsoft_login.html?campaign=CAMP-TEST&variant=V1&user=test-user`

### Production Mode
Deploy to a test server and update tracking URLs in email templates.

## Security Notes

- All pages run in TEST MODE by default
- Credentials are displayed in alerts, never stored
- No data is transmitted to external servers
- Tracking log saved locally to `config/tracking_log.json`

## Customization

Edit the HTML files directly to modify:
- Brand colors and styling
- Company name and logo
- Message text and urgency level
- Landing page behavior

## Integration with Campaign Manager

```python
from scripts.email_sender import CampaignEmailSender, EmailConfig, Recipient

# Configure
config = EmailConfig(
    campaign_id="CAMP-20260831-001",
    test_mode=True,
    from_name="IT Security Team",
    from_email="it-support@company.com"
)

# Create sender
sender = CampaignEmailSender(config)

# Send to recipients
recipients = [
    Recipient(email="user1@company.com", segment="it_staff", variant_id="V1"),
    Recipient(email="user2@company.com", segment="finance", variant_id="V2"),
]

results = sender.send_campaign(recipients, variant_type="urgency", landing_page="microsoft_login.html")

# Get summary
summary = sender.get_summary()
print(json.dumps(summary, indent=2))
```
