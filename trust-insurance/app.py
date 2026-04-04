
# from flask import Flask, render_template, request
# import requests
# import random
# from flask import Flask, render_template, request, redirect, url_for, session

# app = Flask(__name__)
# app.secret_key = "secret123"  # for session management

# API_KEY = "f7b4a3d88337ad2894d3aefc138bf5d0"
# users = {}
# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         users[username] = password
#         return redirect(url_for("login"))

#     return render_template("signup.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         if username in users and users[username] == password:
#             session["user"] = username
#             return redirect(url_for("index"))
#         else:
#             return "Invalid Credentials ❌"

#     return render_template("login.html")
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if "user" not in session:
#         return redirect(url_for("login"))
    
# @app.route("/logout")
# def logout():
#     session.pop("user", None)
#     return redirect(url_for("login"))    

# # 🌦️ Get Weather Data
# def get_weather(city, country):
#     url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}&units=metric"
#     response = requests.get(url).json()
#     print(response)

#     if response.get("cod") != 200:
#         return "Error"

#     return response["weather"][0]["main"]


# # 🚗 Simulated Traffic
# def get_traffic():
#     return random.choice(["Low", "Moderate", "Heavy"])


# # 🧠 Trust Score Calculation (Enhanced)
# def calculate_trust():
#     activity = random.randint(3, 10)
#     gps_variation = random.randint(1, 15)
#     anomaly = random.choice([False, False, False, True])
#     traffic = get_traffic()

#     score = 50

#     # Activity impact
#     if activity >= 6:
#         score += 25
#     else:
#         score += 10

#     # GPS consistency
#     if gps_variation <= 8:
#         score += 20
#     else:
#         score += 5

#     # 🚗 Traffic impact (NEW)
#     if traffic == "Heavy":
#         score += 10
#     elif traffic == "Moderate":
#         score += 5

#     # Anomaly penalty
#     if anomaly:
#         score -= 30

#     return score, activity, gps_variation, anomaly, traffic


# # 🚀 Main Route
# @app.route("/", methods=["GET", "POST"])
# def index():
#     result = None

#     if request.method == "POST":
#         city = request.form["city"]
#         country = request.form["country"]

#         weather = get_weather(city, country)
#         trust_score, activity, gps, anomaly, traffic = calculate_trust()

#         # 🎯 Smart Decision Logic (extended, not changed)
#         if weather in ["Rain", "Thunderstorm"]:
#             if trust_score > 60:
#                 status = "APPROVED ✅"
#                 reason = "Bad weather + sufficient trust score"
#             else:
#                 status = "UNDER REVIEW ⚠️"
#                 reason = "Weather valid but trust score moderate"

#         # 🚗 NEW Traffic-based approval (extra condition)
#         elif traffic == "Heavy" and trust_score > 70:
#             status = "APPROVED ✅"
#             reason = "Heavy traffic disruption + high trust score"

#         elif trust_score > 75:
#             status = "APPROVED ✅"
#             reason = "High trust score despite no major disruption"

#         elif trust_score > 50:
#             status = "UNDER REVIEW ⚠️"
#             reason = "Moderate trust score"

#         else:
#             status = "REJECTED ❌"
#             reason = "Low trust or anomaly detected"

#         result = {
#             "weather": weather,
#             "traffic": traffic,  # NEW
#             "trust_score": trust_score,
#             "status": status,
#             "reason": reason,
#             "activity": activity,
#             "gps": gps,
#             "anomaly": anomaly
#         }

#     return render_template("index.html", result=result)


# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
import requests
import random

app = Flask(__name__)
app.secret_key = "secret123"  # for session management

API_KEY = "f7b4a3d88337ad2894d3aefc138bf5d0"
users = {}

# 🔐 Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password
        return redirect(url_for("login"))

    return render_template("signup.html")


# 🔑 Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return "Invalid Credentials ❌"

    return render_template("login.html")


# 🚪 Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# 🌦️ Get Weather Data
def get_weather(city, country):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    print(response)

    if response.get("cod") != 200:
        return "Error"

    return response["weather"][0]["main"]


# 🚗 Simulated Traffic
def get_traffic():
    return random.choice(["Low", "Moderate", "Heavy"])


# 🧠 Trust Score Calculation
def calculate_trust():
    activity = random.randint(3, 10)
    gps_variation = random.randint(1, 15)
    anomaly = random.choice([False, False, False, True])
    traffic = get_traffic()

    score = 50

    if activity >= 6:
        score += 25
    else:
        score += 10

    if gps_variation <= 8:
        score += 20
    else:
        score += 5

    if traffic == "Heavy":
        score += 10
    elif traffic == "Moderate":
        score += 5

    if anomaly:
        score -= 30

    return score, activity, gps_variation, anomaly, traffic


# 🚀 Main Route (ONLY ONE INDEX)
@app.route("/", methods=["GET", "POST"])
def index():
    # 🔐 Protect route
    if "user" not in session:
        return redirect(url_for("login"))

    result = None

    if request.method == "POST":
        city = request.form["city"]
        country = request.form["country"]

        weather = get_weather(city, country)
        trust_score, activity, gps, anomaly, traffic = calculate_trust()

        # 🎯 Decision Logic
        if weather in ["Rain", "Thunderstorm"]:
            if trust_score > 60:
                status = "APPROVED ✅"
                reason = "Bad weather + sufficient trust score"
            else:
                status = "UNDER REVIEW ⚠️"
                reason = "Weather valid but trust score moderate"

        elif traffic == "Heavy" and trust_score > 70:
            status = "APPROVED ✅"
            reason = "Heavy traffic disruption + high trust score"

        elif trust_score > 75:
            status = "APPROVED ✅"
            reason = "High trust score despite no major disruption"

        elif trust_score > 50:
            status = "UNDER REVIEW ⚠️"
            reason = "Moderate trust score"

        else:
            status = "REJECTED ❌"
            reason = "Low trust or anomaly detected"

        result = {
            "weather": weather,
            "traffic": traffic,
            "trust_score": trust_score,
            "status": status,
            "reason": reason,
            "activity": activity,
            "gps": gps,
            "anomaly": anomaly
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)