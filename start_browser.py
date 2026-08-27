"""Launcher for Knight-Shade browser API."""
import sys
sys.path.insert(0, r"C:\Users\Project Zero\ai-workstation")
from browser.api import app, get_engine
import uvicorn
print(f"[knight-shade] Session: {get_engine().session_id}")
uvicorn.run(app, host="0.0.0.0", port=8180)
