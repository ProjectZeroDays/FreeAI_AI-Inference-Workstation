---
name: quantum-launcher
description: Starts and verifies the Quantum framework. Handles Flask app, Python GUI, and backend API startup with health checks. Use when the user wants to launch, restart, or verify the framework is running.
---

# Quantum Launcher

Starts the Quantum framework components and verifies they are operational.

## Launch Commands (Priority Order)

```bash
# 1. Primary entry point
cd "C:\Users\Project Zero\Desktop\Quantum" && python run_quantum.py 2>&1

# 2. Flask web interface only
python core/web_interface/app.py

# 3. Direct app runner
python run_app.py

# 4. Full initialization + run
python initialize_and_run.py
```

## Health Checks After Launch

```bash
# Test Flask is responding
curl -s -o /dev/null -w "%{http_code}" https://localhost:4433/ 2>/dev/null || echo "Flask not responding"

# Test API endpoint
curl -s -k https://localhost:4433/api/status 2>/dev/null

# Test WebSocket
# ws://localhost:8765 should accept connections

# Test imports
python test_imports.py
```

## Port Map

| Service | Port | Protocol |
|---------|------|----------|
| Flask Web UI | 4433 | HTTPS |
| HTTP Redirect | 8080 | HTTP→HTTPS |
| Backend API | 5000 | HTTP |
| WebSocket | 8765 | WS |
| Python GUI | N/A | tkinter window |

## Common Issues

- **Auth errors on Flask**: Non-fatal. Python GUI launches independently.
- **Port 4433 in use**: Kill existing process: `netstat -ano | findstr :4433` then `taskkill /PID <pid> /F`
- **Module import errors**: Run `python test_imports.py` to isolate which module fails
- **GGUF not loading**: Check `configs/mimocode_config.json` has correct `model_path` and `binary_path`
- **SSL certificate**: Flask uses self-signed cert. Access via `https://localhost:4433` (accept warning)

## Startup Sequence

1. Check if any Quantum process already running (avoid duplicates)
2. Start Flask web interface on port 4433
3. Start Python GUI (tkinter window)
4. Verify WebSocket server on port 8765
5. Run health check: `python test_imports.py`
6. Report status to user
