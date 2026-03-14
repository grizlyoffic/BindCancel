from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.30",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

APP_ID = "100067"
REGION = "PK"
LOCALE = "en_PK"

def call_post(url, data):
    try:
        resp = requests.post(url, headers=HEADERS, data=data)
        return resp.json()
    except:
        return {"error": "Request failed"}

# ------------------------- Bind Info -------------------------
@app.route("/info", methods=["GET"])
def bind_info():
    access_token = request.args.get("access_token")
    if not access_token:
        return jsonify({"error":"access_token required"}),400
    url = f"https://bind-info-nu.vercel.app/bind_info?access_token={access_token}"
    try:
        resp = requests.get(url)
        return resp.json()
    except:
        return {"error": "Failed to fetch bind info"}

# ------------------------- Send OTP -------------------------
@app.route("/send_otp", methods=["GET"])
def send_otp():
    access_token = request.args.get("access_token")
    email = request.args.get("email")
    if not access_token or not email:
        return jsonify({"error":"access_token and email required"}),400

    url_send = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
    payload = {"email": email, "app_id": APP_ID, "access_token": access_token, "locale": LOCALE, "region": REGION}
    res = call_post(url_send, payload)
    return res

# ------------------------- Unbind -------------------------
@app.route("/unbind", methods=["GET"])
def unbind():
    access_token = request.args.get("access_token")
    email = request.args.get("email")
    otp = request.args.get("otp")
    if not access_token or not email or not otp:
        return jsonify({"error":"access_token, email, otp required"}),400

    # Verify OTP → identity_token
    res_identity = call_post(
        "https://100067.connect.garena.com/game/account_security/bind:verify_identity",
        {"email": email, "app_id": APP_ID, "access_token": access_token, "otp": otp}
    )
    identity_token = res_identity.get("identity_token")
    if not identity_token:
        return jsonify({"error":"identity verification failed","raw":res_identity}),400

    # Create unbind request
    res_unbind = call_post(
        "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request",
        {"app_id": APP_ID, "access_token": access_token, "identity_token": identity_token}
    )
    return res_unbind

# ------------------------- Cancel Bind -------------------------
@app.route("/cancel", methods=["GET"])
def cancel():
    access_token = request.args.get("access_token")
    if not access_token:
        return jsonify({"error":"access_token required"}),400

    res_cancel = call_post(
        "https://100067.connect.gopapi.io/game/account_security/bind:cancel_request",
        {"app_id": APP_ID, "access_token": access_token}
    )
    return res_cancel

# ------------------------- Change Bind (5 Steps) -------------------------
@app.route("/change", methods=["GET"])
def change():
    access_token = request.args.get("access_token")
    old_email = request.args.get("old_email")
    old_otp = request.args.get("old_otp")
    new_email = request.args.get("new_email")
    new_otp = request.args.get("new_otp")

    if not all([access_token, old_email, old_otp, new_email, new_otp]):
        return jsonify({"error":"access_token, old_email, old_otp, new_email, new_otp required"}),400

    # Step 2: Verify old email OTP → identity_token
    res_identity = call_post(
        "https://100067.connect.garena.com/game/account_security/bind:verify_identity",
        {"email": old_email,"app_id":APP_ID,"access_token":access_token,"otp":old_otp}
    )
    identity_token = res_identity.get("identity_token")
    if not identity_token:
        return jsonify({"error":"identity verification failed","raw":res_identity}),400

    # Step 4: Verify new email OTP → verifier_token
    res_verifier = call_post(
        "https://100067.connect.garena.com/game/account_security/bind:verify_otp",
        {"email": new_email,"app_id":APP_ID,"access_token":access_token,"otp":new_otp}
    )
    verifier_token = res_verifier.get("verifier_token")
    if not verifier_token:
        return jsonify({"error":"verifier token failed","raw":res_verifier}),400

    # Step 5: Create rebind request
    res_rebind = call_post(
        "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request",
        {
            "identity_token": identity_token,
            "email": new_email,
            "app_id": APP_ID,
            "verifier_token": verifier_token,
            "access_token": access_token
        }
    )
    return res_rebind

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)    url = "https://100067.connect.gopapi.io/game/account_security/bind:cancel_request"
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
