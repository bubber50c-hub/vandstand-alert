import os
import requests

API_KEY = os.environ["API_KEY"]
STATION_ID = "22332"
THRESHOLD = -30


def get_latest():
    url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

    params = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "period": "latest-24-hours"
    }

    r = requests.get(url, params=params)

    print("STATUS:", r.status_code)

    data = r.json()

    features = data.get("features", [])
    print("Features:", len(features))

    if not features:
        return None

    # seneste observation
    latest = sorted(features, key=lambda x: x["properties"]["observed"])[-1]

    return {
        "value": latest["properties"]["value"],
        "time": latest["properties"]["observed"]
    }


def main():
    print("SCRIPT STARTER")

    data = get_latest()

    if not data:
        print("No data available")
        return

    print("Latest:", data)

    if data["value"] > THRESHOLD:
        print("🚨 ALARM")
    else:
        print("OK")


if __name__ == "__main__":
    main()
