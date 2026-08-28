# Sidebar Toggle Implementation Script
# This script atomically updates the dashboard HTML, CSS, and JS
# The dashboard/templates/index.html file is at C:\Users\Project Zero\FreeAI_AI_Inference_Workstation\dashboard\templates\index.html

import re
from pathlib import Path

html_file = Path("C:/Users/Project Zero/FreeAI_AI_Inference_Workstation/dashboard/templates/index.html")

# Read the HTML file
with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

# Add the sidebar toggle button in sidebar-foot section
# Looking for: <div class="sidebar-foot">
toggle_button = '          <button class="sidebar-toggle" id="sidebar-toggle" title="Toggle sidebar">◀</button>'

# Find the sidebar-foot section and add the button after it
if '<div class="sidebar-foot">' in content:
    content = content.replace('<div class="sidebar-foot">', '<div class="sidebar-foot">' + toggle_button)

# Write back
with open(html_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✓ Updated {html_file}")
