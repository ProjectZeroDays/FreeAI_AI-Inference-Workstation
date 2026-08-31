#!/usr/bin/env python3
"""
Standalone landing page server for campaign testing
Serves phishing simulation pages with tracking
"""

import http.server
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime


class TrackingHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that tracks page visits"""
    
    tracking_log = []
    landing_pages_dir = None
    
    def __init__(self, *args, **kwargs):
        if self.landing_pages_dir is None:
            self.landing_pages_dir = Path(__file__).parent.parent / "templates" / "landing_pages"
        super().__init__(*args, directory=str(self.landing_pages_dir), **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Log tracking data
        if params:
            tracking_entry = {
                "timestamp": datetime.now().isoformat(),
                "path": parsed.path,
                "params": params,
                "client_ip": self.client_address[0]
            }
            self.tracking_log.append(tracking_entry)
            
            # Save tracking log
            log_file = Path(__file__).parent.parent / "config" / "tracking_log.json"
            with open(log_file, "w") as f:
                json.dump(self.tracking_log, f, indent=2)
            
            print(f"\n📊 Tracking: {tracking_entry['params'].get('campaign', ['unknown'])[0]}")
            print(f"   Variant: {tracking_entry['params'].get('variant', ['unknown'])[0]}")
            print(f"   User: {tracking_entry['params'].get('user', ['unknown'])[0]}")
            print(f"   IP: {tracking_entry['client_ip']}")
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Campaign Landing Page Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--page", default="microsoft_login.html", 
                       choices=["microsoft_login.html", "google_workspace.html", "adobe_sign.html"])
    parser.add_argument("--campaign", default="CAMP-TEST-001")
    parser.add_argument("--variant", default="V1")
    parser.add_argument("--user", default="test-user")
    
    args = parser.parse_args()
    
    print(f"\n🌐 Campaign Landing Page Server")
    print(f"{'='*50}")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Page: {args.page}")
    print(f"Campaign: {args.campaign}")
    print(f"Variant: {args.variant}")
    print()
    
    # Build URL with tracking params
    base_url = f"http://{args.host}:{args.port}/{args.page}"
    tracking_url = f"{base_url}?campaign={args.campaign}&variant={args.variant}&user={args.user}"
    
    print(f"📧 Testing URL: {tracking_url}")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    # Start server
    server = http.server.HTTPServer((args.host, args.port), TrackingHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        
        # Print tracking summary
        log_file = Path(__file__).parent.parent / "config" / "tracking_log.json"
        if log_file.exists():
            with open(log_file) as f:
                log = json.load(f)
            print(f"\n📊 Tracking Summary:")
            print(f"   Total visits: {len(log)}")
            for entry in log:
                print(f"   - {entry['timestamp']}: {entry['params'].get('variant', ['?'])[0]}")


if __name__ == "__main__":
    main()
