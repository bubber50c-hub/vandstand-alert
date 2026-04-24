import os
import requests
from datetime import datetime, timedelta

# -----------------------
# CONFIG
# -----------------------
API_KEY = os.environ["API_KEY"]

# Aarhus station (observation fallback virker stabilt her)
STATION_ID = "22332"

THRESHOLD = -30  # cm


# -----------------------
# API CALL
# -----------------------
def fetch(endpoint, params):
    url = f"https://opendataapi.dmi.dk/v2/oceanObs/collections/{endpoint}/items"

    r = requests.get(url, params=params)

    print(f"{endpoint} STATUS:", r.status_code)

    if r.status_code != 200:
        print("ERROR:", r.text)
        return []

    data = r.json()
    return data.get("features", [])


# -----------------------
# GET DATA (forecast → fallback)
# -----------------------
def get_data():
    # ---------------- FORECAST ----------------
    params_forecast = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "predictionType": "10minutes",
        "limit": 100
    }

    features = fetch("tidewater", params_forecast)

    print("Forecast points:", len(features))

    if features:
        return [
            {
                "value": f["properties"]["value"],
                "time": f["properties"]["predictionTime"]
            }
            for f in features
            if f.get("properties", {}).get("value") is not None
        ]

    # ---------------- OBSERVATION FALLBACK ----------------
    print("Fallback to observations")

    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)

    params_obs = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "datetime": f"{yesterday.isoformat()}Z/{now.isoformat()}Z",
        "limit": 100
    }

    features = fetch("observation", params_obs)

    print("Observation points:", len(features))

    return [
        {
            "value": f["properties"]["value"],
            "time": f["properties"]["observed"]
        }
        for f in features
        if f.get("properties", {}).get("value") is not None
    ]


# -----------------------
# MAIN LOGIC
# -----------------------
def main():
    print("SCRIPT STARTER")

    data = get_data()

    if not data:
        print("No data available")
        return

    # 👉 Brug SENESTE måling (ikke max fra 1992 😄)
    latest = sorted(data, key=lambda x: x["time"])[-1]

    print("Latest:", latest)

    if latest["value"] > THRESHOLD:
        print("🚨 ALARM – vandstand over threshold")
    else:
        print("OK")


if __name__ == "__main__":
    main()
