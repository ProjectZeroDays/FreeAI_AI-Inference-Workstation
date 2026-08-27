"""Quick dashboard launcher — starts Flask + terminal WebSocket server."""
import asyncio
import os
import sys
import threading

from dashboard.backend import app


def run_flask():
    port = int(os.environ.get("DASHBOARD_PORT", "8080"))
    print(f"[dashboard] Flask serving on http://0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    terminal_port = int(os.environ.get("TERMINAL_WS_PORT", "8081"))
    print(f"[launcher] Starting FreeAI Dashboard (Flask :8080 + Terminal WS :{terminal_port})", flush=True)

    # Start Flask in a daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run terminal WebSocket server in main thread
    from dashboard.terminal_server import main as ws_main
    try:
        asyncio.run(ws_main())
    except KeyboardInterrupt:
        print("\n[launcher] Stopping...", flush=True)
        sys.exit(0)
