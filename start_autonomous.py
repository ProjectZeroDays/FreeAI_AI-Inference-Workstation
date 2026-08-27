"""Launcher for autonomous SDLC API."""
import sys
sys.path.insert(0, r"C:\Users\Project Zero\ai-workstation")
from autonomous import api
import uvicorn
uvicorn.run(api.app, host="0.0.0.0", port=8050)
