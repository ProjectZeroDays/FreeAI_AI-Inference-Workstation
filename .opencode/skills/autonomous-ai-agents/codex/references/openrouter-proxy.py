#!/usr/bin/env python3
"""
OpenRouter Proxy for Codex CLI
Run this proxy to enable Codex to work with OpenRouter via binary patching.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error
import sys
import os

# Configuration - modify these values
API_KEY = os.environ.get('OPENROUTER_API_KEY', 'REDACTED
OPENROUTER_BASE = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
LISTEN_HOST = os.environ.get('OPENROUTER_PROXY_HOST', 'localhost')
LISTEN_PORT = int(os.environ.get('OPENROUTER_PROXY_PORT', '8080'))

class OpenRouterProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.handle_request()
    
    def do_GET(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Construct target URL
            url = OPENROUTER_BASE + self.path
            
            # Prepare headers for OpenRouter
            headers = {}
            for key, value in self.headers.items():
                key_lower = key.lower()
                # Skip hop-by-hop headers and host
                if key_lower in ['host', 'content-length', 'transfer-encoding', 'connection']:
                    continue
                headers[key] = value
            
            # Add or override Authorization header
            headers['Authorization'] = f'Bearer {API_KEY}'
            
            # Add recommended headers
            headers.setdefault('HTTP-Referer', 'https://hermes.ai')
            headers.setdefault('X-Title', 'Hermes-Agent')
            headers.setdefault('Content-Type', 'application/json')
            
            # Create request to OpenRouter
            req = urllib.request.Request(
                url,
                data=post_data,
                headers=headers,
                method=self.command
            )
            
            # Make request to OpenRouter
            try:
                response = urllib.request.urlopen(req)
                
                # Send response back to client
                self.send_response(response.status)
                for header, value in response.getheaders():
                    # Skip hop-by-hop headers
                    if header.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Copy response body
                response_data = response.read()
                self.wfile.write(response_data)
                
            except urllib.error.HTTPError as e:
                # Handle HTTP errors from OpenRouter
                self.send_response(e.code)
                for header, value in e.headers.items():
                    if header.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.read() if e.length > 0 else self.wfile.write(b'')
                
            except urllib.error.URLError as e:
                # Handle connection errors
                self.send_error(502, f"Bad Gateway: {str(e)}")
                
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def log_message(self, format, *args):
        # Log to stderr instead of stdout
        sys.stderr.write("%s - - [%s] %s\n" % (
            self.address_string(),
            self.log_date_time_string(),
            format%args
        ))

def main():
    print(f"Starting OpenRouter proxy for Codex CLI")
    print(f"Listening on: http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"Forwarding to: {OPENROUTER_BASE}")
    print(f"Using API key: {API_KEY[:20]}...")
    print("")
    print("To use with patched Codex binary:")
    print(f"  export OPENAI_API_BASE_URL=http://{LISTEN_HOST}:{LISTEN_PORT}/v1")
    print("  ./codex-patched exec 'your prompt'")
    print("")
    print("Press Ctrl+C to stop the proxy")
    
    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), OpenRouterProxyHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy...")
        server.server_close()

if __name__ == '__main__':
    main()