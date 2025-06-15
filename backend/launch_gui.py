#!/usr/bin/env python3
"""
Simple GUI launcher for Aura Control Panel
"""

import webbrowser
import http.server
import socketserver
from pathlib import Path
import threading
import time

def serve_dashboard():
    """Serve the dashboard HTML file"""
    web_dir = Path("gui/frontend")
    if not web_dir.exists():
        web_dir = Path(".")
    
    os.chdir(web_dir)
    
    with socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler) as httpd:
        print("🌐 Aura Control Panel running at: http://localhost:8000")
        httpd.serve_forever()

def main():
    print("🚀 Launching Aura Control Panel...")
    
    # Start web server in background
    server_thread = threading.Thread(target=serve_dashboard, daemon=True)
    server_thread.start()
    
    # Wait a moment then open browser
    time.sleep(2)
    webbrowser.open("http://localhost:8000")
    
    print("✅ Aura Control Panel launched!")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Aura Control Panel")

if __name__ == "__main__":
    import os
    main()