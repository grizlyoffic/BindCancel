from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.30",
    "Content-Type": "application/x-www-form-urlencoded"
}

APP_ID = "100067"

# ---------------- BIND INFO ----------------

@app.route("/bindinfo")
def bindinfo():

    token = request.args.get("access_token")

    url = f"https://bind-info-nu.vercel.app/bind_info?access_token={token}"

    r = requests.get(url)

    return jsonify(r.json())


# ---------------- UNBIND FLOW ----------------

@app.route("/unbind")
def unbind():

    token = request.args.get("access_token")
    email = request.args.get("email")
    otp = request.args.get("otp")

    if not token or not email:
        return jsonify({"error":"access_token and email required"})

    # STEP 1 OTP SEND
    if not otp:

        url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"

        data = {
            "email":email,
            "locale":"en_PK",
            "region":"PK",
            "app_id":APP_ID,
            "access_token":token
        }

        r = requests.post(url,headers=HEADERS,data=data)

        return jsonify({
            "step":"otp_sent",
            "response":r.json()
        })

    # STEP 2 VERIFY + UNBIND

    url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"

    data = {
        "email":email,
        "otp":otp,
        "app_id":APP_ID,
        "access_token":token
    }

    r = requests.post(url,headers=HEADERS,data=data)

    js = r.json()

    if js.get("result") != 0:
        return jsonify(js)

    identity_token = js.get("identity_token")

    url2 = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"

    data2 = {
        "app_id":APP_ID,
        "access_token":token,
        "identity_token":identity_token
    }

    r2 = requests.post(url2,headers=HEADERS,data=data2)

    return jsonify({
        "step":"unbind_request_created",
        "verify":js,
        "unbind":r2.json()
    })


# ---------------- CANCEL BIND ----------------

@app.route("/cancelbind")
def cancelbind():

    token = request.args.get("access_token")

    url = "https://100067.connect.gopapi.io/game/account_security/bind:cancel_request"

    data = {
        "app_id":APP_ID,
        "access_token":token
    }

    r = requests.post(url,headers=HEADERS,data=data)

    return jsonify(r.json())


# ---------------- CHANGE BIND FLOW ----------------

@app.route("/change")
def change():

    token = request.args.get("access_token")
    old_email = request.args.get("old_email")
    otp = request.args.get("otp")
    new_email = request.args.get("new_email")
    notp = request.args.get("notp")

    if not token or not old_email:
        return jsonify({"error":"access_token and old_email required"})


    # STEP 1 SEND OTP OLD EMAIL

    if not otp:

        url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"

        data = {
            "email":old_email,
            "locale":"en_PK",
            "region":"PK",
            "app_id":APP_ID,
            "access_token":token
        }

        r = requests.post(url,headers=HEADERS,data=data)

        return jsonify({
            "step":"otp_sent_old_email",
            "response":r.json()
        })


    # STEP 2 VERIFY OLD EMAIL

    url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"

    data = {
        "email":old_email,
        "otp":otp,
        "app_id":APP_ID,
        "access_token":token
    }

    r = requests.post(url,headers=HEADERS,data=data)

    js = r.json()

    if js.get("result") != 0:
        return jsonify(js)

    identity_token = js.get("identity_token")


    # STEP 3 SEND OTP NEW EMAIL

    if new_email and not notp:

        url2 = "https://100067.connect.garena.com/game/account_security/bind:send_otp"

        data2 = {
            "email":new_email,
            "locale":"en_PK",
            "region":"PK",
            "app_id":APP_ID,
            "access_token":token
        }

        r2 = requests.post(url2,headers=HEADERS,data=data2)

        return jsonify({
            "step":"otp_sent_new_email",
            "identity_token":identity_token,
            "response":r2.json()
        })


    # STEP 4 VERIFY NEW EMAIL + REBIND

    if new_email and notp:

        url3 = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"

        data3 = {
            "email":new_email,
            "otp":notp,
            "app_id":APP_ID,
            "access_token":token
        }

        r3 = requests.post(url3,headers=HEADERS,data=data3)

        js2 = r3.json()

        if js2.get("result") != 0:
            return jsonify(js2)

        verifier_token = js2.get("verifier_token")

        url4 = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"

        data4 = {
            "identity_token":identity_token,
            "email":new_email,
            "app_id":APP_ID,
            "verifier_token":verifier_token,
            "access_token":token
        }

        r4 = requests.post(url4,headers=HEADERS,data=data4)

        return jsonify({
            "step":"rebind_created",
            "verify_new":js2,
            "rebind":r4.json()
        })

    return jsonify({"message":"missing parameters"})
    

if __name__ == "__main__":
    app.run()
