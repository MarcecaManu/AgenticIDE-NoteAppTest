#!/usr/bin/env python3
"""
Startup script for the File Upload & Management System frontend
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS support"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_server(port=3000):
    """Start the HTTP server for the frontend"""
    script_dir = Path(__file__).parent
    frontend_dir = script_dir / "frontend"
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    print("🌐 Starting File Upload & Management System Frontend...")
    print(f"📁 Serving files from: {frontend_dir}")
    print(f"🔗 Frontend available at: http://localhost:{port}")
    print("🔄 Make sure the backend is running at http://localhost:8000")
    print("\n" + "="*50)
    
    # Create and start the server
    server = HTTPServer(('localhost', port), CORSHTTPRequestHandler)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{port}')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        print(f"🚀 Server started successfully!")
        print("🌍 Opening browser...")
        print("\n💡 Press Ctrl+C to stop the server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        server.shutdown()
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    port = 3000
    
    # Check if port is already in use
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            print(f"⚠️  Port {port} is already in use. Trying port {port + 1}...")
            port += 1
    
    start_server(port)

if __name__ == "__main__":
    main()
