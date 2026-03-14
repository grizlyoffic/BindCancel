# api/index.py
from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        # Check if cancelbind parameter exists
        if 'cancelbind' not in params:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "success": False,
                "error": "cancelbind parameter required. Use ?cancelbind={access_token}"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        access_token = params['cancelbind'][0]
        
        try:
            # STEP 1: Get bind info
            info_url = f"https://bind-info-nu.vercel.app/bind_info?access_token={access_token}"
            
            info_response = requests.get(info_url)
            info_data = info_response.json()
            
            email = None
            try:
                email = info_data["data"]["current_email"]
            except:
                pass
            
            # STEP 2: Cancel bind request
            url = "https://100067.connect.gopapi.io/game/account_security/bind:cancel_request"
            
            headers = {
                "User-Agent": "GarenaMSDK/4.0.30",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            data = {
                "app_id": "100067",
                "access_token": access_token
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            # Prepare response
            result = {
                "success": False,
                "status_code": response.status_code,
                "email": email
            }
            
            # Check if successful
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("result") == 0:
                    result["success"] = True
                    result["message"] = "Successfully Cancel Bind"
                else:
                    result["error"] = response_data.get("message", "Unknown error")
            else:
                result["error"] = f"HTTP {response.status_code}"
            
            # Try to parse response as JSON
            try:
                result["server_response"] = response.json()
            except:
                result["server_response"] = response.text
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "success": False,
                "error": str(e)
            }
            self.wfile.write(json.dumps(response).encode())
