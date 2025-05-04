import streamlit as st
import json
import os
from streamlit.web.server import Server
from streamlit.runtime.scriptrunner import get_script_run_ctx
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse

# Path to JSON file
BLOCKS_FILE = "blocks.json"

# Initialize blocks.json if it doesn't exist
def init_blocks():
    if not os.path.exists(BLOCKS_FILE):
        default_blocks = [
            {"name": "", "phone": "", "email": "", "services": "", "rating": 0}
            for _ in range(6)
        ]
        with open(BLOCKS_FILE, "w") as f:
            json.dump({"blocks": default_blocks}, f)

init_blocks()

# HTTP server to handle API requests
class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_blocks':
            try:
                with open(BLOCKS_FILE, "r") as f:
                    data = json.load(f)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/save_block':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request = json.loads(post_data.decode())
                block = request['block']
                index = request['index']

                with open(BLOCKS_FILE, "r") as f:
                    data = json.load(f)
                
                if index is not None and 0 <= index < len(data["blocks"]):
                    data["blocks"][index] = block
                else:
                    data["blocks"].append(block)
                
                with open(BLOCKS_FILE, "w") as f:
                    json.dump(data, f)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Start HTTP server in a separate thread
def start_api_server():
    server = HTTPServer(('0.0.0.0', 8000), APIHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

# Run API server
start_api_server()

# Streamlit app
st.set_page_config(page_title="Company Information Directory", layout="wide")

# Render index.html
with open("index.html", "r") as file:
    html_content = file.read()
st.components.v1.html(html_content, height=1000, scrolling=True)