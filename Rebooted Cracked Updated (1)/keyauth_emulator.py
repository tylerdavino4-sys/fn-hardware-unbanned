#!/usr/bin/env python3
"""
KeyAuth SSL Emulator - Runs on port 443 with HTTPS
Handles KeyAuth API endpoints for REBOOTEDSPOOFER
"""
import ssl
import json
import http.server
import urllib.parse
import sys
import os
import tempfile
import subprocess

CERT_DIR = os.path.dirname(os.path.abspath(__file__))
PFX_FILE = os.path.join(CERT_DIR, 'server.pfx')
CERT_FILE = os.path.join(CERT_DIR, 'server.crt')
KEY_FILE = os.path.join(CERT_DIR, 'server.key')

def create_ssl_context():
    """Create SSL context using cert file"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # The PFX contains the private key; .crt is the public cert
    # For Python 3.12+ we can extract from PFX if cryptography is available
    # Otherwise use the .crt file for verification (won't work for SSL server)
    # Let's try to load the PFX directly
    
    # Export key from PFX using certutil or openssl if available
    key_path = KEY_FILE
    if not os.path.exists(key_path):
        # Try to extract key from PFX using certutil
        try:
            # certutil can export to PEM
            result = subprocess.run(
                ['certutil', '-p', 'bypass', '-exportPFX', PFX_FILE, 'temp.pfx'],
                capture_output=True, text=True, shell=True
            )
        except:
            pass
    
    try:
        context.load_cert_chain(CERT_FILE)  # public cert
        # If this fails, we need the key separately
    except:
        print("[!] Failed to load cert chain. Need separate key file.")
        
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

class KeyAuthHandler(http.server.BaseHTTPRequestHandler):
    def log_request_data(self, method, path, body=""):
        print(f"[{method}] {path}")
        if body and len(body) > 2:
            print(f"  Body: {body[:1000]}")
    
    def send_response_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def error_response(self, msg="error"):
        self.send_response_json({"success": False, "message": msg, "error": msg})
    
    def success_response(self, extra=None):
        resp = {
            "success": True,
            "message": "success",
            "token": "bypass_token_here",
            "level": "premium",
            "expiry": "9999999999",
            "subscriptions": [{"name": "lifetime", "expiry": 9999999999}],
            "username": "bypass_user",
            "ip": "127.0.0.1",
            "hwid": "BYPASS-HWID-00000000",
            "numUsers": 999,
            "numOnlineUsers": 1,
            "version": "999.0.0",
            "download": "",
        }
        if extra:
            resp.update(extra)
        self.send_response_json(resp)
    
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_length).decode("utf-8", errors="replace") if content_length > 0 else ""
        self.log_request_data("POST", self.path, body_raw)
        
        # Parse body
        params = {}
        if body_raw.strip().startswith("{"):
            try: params = json.loads(body_raw)
            except: pass
        elif "=" in body_raw:
            try: params = urllib.parse.parse_qs(body_raw)
            except: pass
            # Flatten
            for k in list(params.keys()):
                if isinstance(params[k], list):
                    params[k] = params[k][0]
        
        type_val = params.get("type", params.get("action", "")).lower()
        
        # INIT - KeyAuth session initialization
        if type_val == "init":
            name = params.get("name", "REBOOTED")
            ownerid = params.get("ownerid", "4c3UhKrXDj")
            ver = params.get("ver", "1.0")
            print(f"  >> INIT: name={name}, ownerid={ownerid}, ver={ver}")
            self.send_response_json({
                "success": True,
                "sessionid": "bypass_session_001",
                "contents": "",
                "response": "initialized"
            })
            return
        
        # Login
        if type_val in ["login", "logina", "auth", "authenticate", ""]:
            user = params.get("username", params.get("user", "bypass"))
            pwd = params.get("password", params.get("pass", "bypass"))
            hwid = params.get("hwid", params.get("hash", "BYPASS"))
            print(f"  >> LOGIN: user={user}, pass={pwd}, hwid={hwid}")
            self.success_response({
                "username": user,
                "level": "Premium Lifetime",
            })
        
        # Register
        if type_val in ["register", "signup"]:
            user = params.get("username", "bypass")
            pwd = params.get("password", "bypass")
            key = params.get("key", params.get("license", "key"))
            print(f"  >> REGISTER: user={user}, key={key}")
            self.success_response({"username": user, "key": key})
        
        # License key check / activate
        if type_val in ["license", "activate", "key"]:
            key = params.get("key", params.get("license_key", params.get("license", "UNKNOWN")))
            hwid = params.get("hwid", params.get("hash", "BYPASS"))
            print(f"  >> LICENSE CHECK: key={key}, hwid={hwid}")
            self.success_response({
                "license": key,
                "subscriptions": [{"name": "lifetime", "expiry": 9999999999}]
            })
        
        # HWID check
        if type_val in ["checkhwid", "hwid", "check"]:
            hwid = params.get("hwid", params.get("hash", "BYPASS"))
            print(f"  >> HWID CHECK: {hwid}")
            self.success_response({"hwid": hwid, "valid": True})
        
        # Fetch online users / stats
        if type_val in ["fetchonlineusers", "users", "stats"]:
            self.success_response()
        
        # Fetch version
        if type_val in ["version", "fetchversion", "checkversion"]:
            self.success_response({
                "version": "999.0.0",
                "updateurl": "",
                "updatedownload": ""
            })
        
        # User data
        if type_val in ["fetchuserdata", "userdata", "data"]:
            self.success_response({
                "username": "bypass_user",
                "level": "Premium Lifetime",
                "subscriptions": [{"name": "lifetime", "expiry": 9999999999}]
            })
        
        # Log
        if type_val in ["log", "debug"]:
            print(f"  >> LOG: {params}")
            self.send_response_json({"success": True})
        
        # File download
        if type_val in ["filedownload", "download", "file", "fileexists"]:
            fileid = params.get("fileid", params.get("id", "0"))
            print(f"  >> FILE DOWNLOAD: id={fileid}")
            self.send_response_json({
                "success": True,
                "content": "AA==",
                "data": "Bypassed content"
            })
        
        # Any other endpoint
        print(f"  >> UNKNOWN TYPE: '{type_val}' - returning success")
        print(f"    Full params: {params}")
        self.success_response()
    
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        self.log_request_data("GET", self.path)
        self.success_response()
    
    def log_message(self, format, *args):
        pass

def run_ssl_server(port=443):
    """Run HTTPS server with self-signed cert"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    context.check_hostname = False
    
    server = http.server.HTTPServer(("0.0.0.0", port), KeyAuthHandler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print(f"[*] KeyAuth SSL Emulator running on 0.0.0.0:{port}")
    print(f"[*] Cert: {CERT_FILE}, Key: {KEY_FILE}")
    print(f"[*] Press Ctrl+C to stop")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 443
    run_ssl_server(port)