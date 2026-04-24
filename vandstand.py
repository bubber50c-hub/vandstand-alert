import os
import requests

API_KEY = os.environ["API_KEY"]

STATION_ID = "22332"  # eksempel – skal evt. justeres

THRESHOLD = -30  # cm


def get_forecast():
    url = "https://opendataapi.dmi.dk/v2/oceanObs/collections/tidewaterstation/items/20002"

    params = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "predictionType": "10minutes",
        "limit": 500
    }

    r = requests.get(url, params=params)
    data = r.json()

    forecast = []

    for f in data["features"]:
        v = f["properties"]["value"]
        t = f["properties"]["predictionTime"]

        forecast.append({
            "value": v,
            "time": t
        })

    return forecast


def main():
    forecast = get_forecast()

    peak = max(forecast, key=lambda x: x["value"])

    print("Peak:", peak)

    if peak["value"] > THRESHOLD:
        print("🚨 ALARM")
    else:
        print("OK")


if __name__ == "__main__":
    main()
