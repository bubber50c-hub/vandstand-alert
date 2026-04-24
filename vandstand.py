import os
import requests

API_KEY = os.environ["API_KEY"]

THRESHOLD = -30


def get_data():
    url = "https://opendataapi.dmi.dk/v2/oceanObs/collections/tidewater/items"

    params = {
        "api-key": API_KEY,
        "parameterId": "waterlevel",
        "limit": 100
    }

    r = requests.get(url, params=params)

    print("STATUS:", r.status_code)

    data = r.json()

    features = data.get("features", [])

    print("Features:", len(features))

    if not features:
        return []

    return [
        {
            "value": f["properties"]["value"],
            "time": f["properties"]["time"]
        }
        for f in features
        if "value" in f.get("properties", {})
    ]


def main():
    print("SCRIPT STARTER")

    data = get_data()

    if not data:
        print("No data available")
        return

    latest = sorted(data, key=lambda x: x["time"])[-1]

    print("Latest:", latest)

    if latest["value"] > THRESHOLD:
        print("🚨 ALARM")
    else:
        print("OK")


if __name__ == "__main__":
    main()
