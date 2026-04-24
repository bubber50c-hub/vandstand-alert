import os
import requests

API_KEY = os.environ["API_KEY"]
STATION_ID = "22332"  # Aarhus virker til observation
THRESHOLD = -30


def fetch(endpoint, params):
    url = f"https://opendataapi.dmi.dk/v2/oceanObs/collections/{endpoint}/items"

    r = requests.get(url, params=params)

    print(f"{endpoint} STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return []

    data = r.json()
    return data.get("features", [])


def get_data():
    # 1. prøv forecast
    params = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "predictionType": "10minutes",
        "limit": 50
    }

    features = fetch("tidewater", params)

    print("Forecast points:", len(features))

    if features:
        return [
            {
                "value": f["properties"]["value"],
                "time": f["properties"]["predictionTime"]
            }
            for f in features
        ]

    # 2. fallback til observation
    print("Fallback to observations")

    params = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "limit": 50
    }

    features = fetch("observation", params)

    print("Observation points:", len(features))

    return [
        {
            "value": f["properties"]["value"],
            "time": f["properties"]["observed"]
        }
        for f in features
    ]


def main():
    print("SCRIPT STARTER")

    data = get_data()

    if not data:
        print("No data at all")
        return

    peak = max(data, key=lambda x: x["value"])

    print("Peak:", peak)

    if peak["value"] > THRESHOLD:
        print("🚨 ALARM")
    else:
        print("OK")


if __name__ == "__main__":
    main()
