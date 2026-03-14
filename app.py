from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

APP_ID = "100067"
HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.30",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

# ------------------- CHANGE BIND -------------------
@app.route("/change", methods=["GET"])
def change_bind():
    token = request.args.get("access_token")
    old_email = request.args.get("old_email")
    otp = request.args.get("otp")
    new_email = request.args.get("new_email")
    notp = request.args.get("notp")  # OTP for new email

    if not token or not old_email:
        return jsonify({"message":"missing parameters: access_token or old_email"}),400

    # Step 1: Send OTP to old email
    if not otp:
        url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
        data = {"email":old_email,"locale":"en_PK","region":"PK","app_id":APP_ID,"access_token":token}
        r = requests.post(url, headers=HEADERS, data=data)
        return jsonify(r.json())

    # Step 2: Verify OTP of old email
    if otp and not new_email:
        url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
        data = {"email":old_email,"otp":otp,"app_id":APP_ID,"access_token":token}
        r = requests.post(url, headers=HEADERS, data=data)
        js = r.json()
        if js.get("result") != 0:
            return jsonify(js)
        identity_token = js.get("identity_token")
        return jsonify({"step":"old_email_verified","identity_token":identity_token})

    # Step 3: Send OTP to new email
    if new_email and not notp:
        url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
        data = {"email":new_email,"locale":"en_PK","region":"PK","app_id":APP_ID,"access_token":token}
        r = requests.post(url, headers=HEADERS, data=data)
        return jsonify(r.json())

    # Step 4: Verify OTP of new email and create rebind request
    if new_email and notp:
        # First verify OTP
        url_verify = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
        data = {"email":new_email,"otp":notp,"app_id":APP_ID,"access_token":token}
        r = requests.post(url_verify, headers=HEADERS, data=data)
        js = r.json()
        if js.get("result") != 0:
            return jsonify(js)
        verifier_token = js.get("verifier_token")
        identity_token = request.args.get("identity_token")
        if not identity_token:
            return jsonify({"message":"identity_token missing, verify old email first"}),400
        # Rebind request
        url_rebind = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
        data_rebind = {"app_id":APP_ID,"access_token":token,"identity_token":identity_token,"email":new_email,"verifier_token":verifier_token}
        r = requests.post(url_rebind, headers=HEADERS, data=data_rebind)
        return jsonify(r.json())

    return jsonify({"message":"missing parameters"}),400

# ------------------- UNBIND EMAIL -------------------
@app.route("/unbind", methods=["GET"])
def unbind_email():
    token = request.args.get("access_token")
    email = request.args.get("email")
    otp = request.args.get("otp")
    if not token or not email:
        return jsonify({"message":"missing parameters: access_token or email"}),400

    # Step 1: Send OTP
    if not otp:
        url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
        data = {"email":email,"locale":"en_PK","region":"PK","app_id":APP_ID,"access_token":token}
        r = requests.post(url, headers=HEADERS, data=data)
        return jsonify(r.json())

    # Step 2: Verify OTP
    url_verify = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
    data = {"email":email,"otp":otp,"app_id":APP_ID,"access_token":token}
    r = requests.post(url_verify, headers=HEADERS, data=data)
    js = r.json()
    if js.get("result") != 0:
        return jsonify(js)
    identity_token = js.get("identity_token")

    # Step 3: Create unbind request
    url_unbind = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
    data_unbind = {"app_id":APP_ID,"access_token":token,"identity_token":identity_token}
    r = requests.post(url_unbind, headers=HEADERS, data=data_unbind)
    return jsonify(r.json())

# ------------------- CANCEL BIND -------------------
@app.route("/cancelbind", methods=["GET"])
def cancel_bind():
    token = request.args.get("access_token")
    if not token:
        return jsonify({"message":"missing parameters: access_token"}),400
    url = "https://100067.connect.gopapi.io/game/account_security/bind:cancel_request"
    data = {"app_id":APP_ID,"access_token":token}
    r = requests.post(url, headers=HEADERS, data=data)
    return jsonify(r.json())

# ------------------- BIND INFO -------------------
@app.route("/info", methods=["GET"])
def bind_info():
    token = request.args.get("access_token")
    if not token:
        return jsonify({"message":"missing parameters: access_token"}),400
    url = f"https://bind-info-nu.vercel.app/bind_info?access_token={token}"
    r = requests.get(url)
    return jsonify(r.json())

if __name__ == "__main__":
    app.run()
