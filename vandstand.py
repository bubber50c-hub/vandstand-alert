import requests
import smtplib
import json
import os
import time
import subprocess
from email.mime.text import MIMEText

# -----------------------
# ENV VARIABLES (GitHub Secrets)
# -----------------------
API_KEY = os.environ["API_KEY"]
EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["EMAIL_PASSWORD"]
RECEIVER = os.environ["RECEIVER"]

# -----------------------
# SETTINGS
# -----------------------
LAT = 56.15
LON = 10.22

THRESHOLD = -30  # cm
STATE_FILE = "alert_state.json"

COOLDOWN_SECONDS = 6 * 60 * 60  # 6 timer


# -----------------------
# FETCH FORECAST
# -----------------------
def get_forecast():
    url = "https://dmigw.govcloud.dk/v1/forecastedr/collections/ocean_forecast/position"

    params = {
        "api-key": API_KEY,
        "coords": f"POINT({LON} {LAT})",
        "parameter-name": "water_level",
    }

    r = requests.get(url, params=params)
    data = r.json()

    values = data["ranges"]["water_level"]["values"]
    times = data["domain"]["axes"]["t"]["values"]

    forecast = []
    for v, t in zip(values, times):
        if v is not None:
            forecast.append({
                "value_cm": v * 100,
                "time": t
            })

    return forecast


# -----------------------
# FIND PEAK
# -----------------------
def find_peak(forecast):
    return max(forecast, key=lambda x: x["value_cm"])


# -----------------------
# TIME FORMAT
# -----------------------
def format_time(iso_time):
    from datetime import datetime
    dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    return dt.strftime("%d-%m %H:%M")


# -----------------------
# STATE HANDLING
# -----------------------
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"alert_active": False, "last_sent": 0}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# -----------------------
# EMAIL
# -----------------------
def send_email(peak):
    msg = MIMEText(
        f"⚠️ Vandstands-prognose Aarhus\n\n"
        f"Peak: {peak['value_cm']:.1f} cm\n"
        f"Tidspunkt: {format_time(peak['time'])}\n"
    )

    msg["Subject"] = f"Vandstand alarm ({peak['value_cm']:.0f} cm)"
    msg["From"] = EMAIL
    msg["To"] = RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)


# -----------------------
# GIT COMMIT STATE
# -----------------------
def git_commit():
    subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
    subprocess.run(["git", "add", STATE_FILE])
    subprocess.run(["git", "commit", "-m", "update state"], check=False)
    subprocess.run(["git", "push"], check=False)


# ----------------------
# MAIN LOGIC
# -----------------------
def main():
    try:
        forecast = get_forecast()
        peak = find_peak(forecast)

        state = load_state()
        now = time.time()

        print(f"Peak: {peak['value_cm']:.1f} cm")
        print(f"Alert active: {state['alert_active']}")

        over_threshold = peak["value_cm"] > THRESHOLD
        cooldown_ok = (now - state["last_sent"]) > COOLDOWN_SECONDS

        if over_threshold:
            if not state["alert_active"] and cooldown_ok:
                print("🚨 Sending alert")
                send_email(peak)
                state["alert_active"] = True
                state["last_sent"] = now
            else:
                print("No new alert (already active or cooldown)")

        else:
            if state["alert_active"]:
                print("✅ Back to normal – resetting state")
            state["alert_active"] = False

        save_state(state)
        git_commit()

    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
