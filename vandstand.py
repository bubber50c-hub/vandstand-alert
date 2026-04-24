import os
import requests

# -----------------------
# CONFIG
# -----------------------
API_KEY = os.environ["API_KEY"]

# ⚠️ Skift hvis nødvendigt
STATION_ID = "22332"

THRESHOLD = -30  # cm


# -----------------------
# FETCH DATA
# -----------------------
def get_forecast():
    url = "https://opendataapi.dmi.dk/v2/oceanObs/collections/tidewater/items"

    params = {
        "api-key": API_KEY,
        "stationId": STATION_ID,
        "predictionType": "10minutes",
        "limit": 200
    }

    headers = {
        "Accept": "application/json"
    }

    r = requests.get(url, params=params, headers=headers)

    print("STATUS:", r.status_code)

    if r.status_code != 200:
        print("ERROR RESPONSE:")
        print(r.text)
        return []

    data = r.json()

    # Debug: hvor mange datapunkter får vi?
    features = data.get("features", [])
    print("Number of features:", len(features))

    if not features:
        print("No data returned from API")
        return []

    forecast = []

    for f in features:
        props = f.get("properties", {})

        value = props.get("value")
        time = props.get("predictionTime")

        if value is not None:
            forecast.append({
                "value": value,
                "time": time
            })

    return forecast


# -----------------------
# MAIN
# -----------------------
def main():
    print("SCRIPT STARTER")

    forecast = get_forecast()

    if not forecast:
        print("No usable data")
        return

    peak = max(forecast, key=lambda x: x["value"])

    print("Peak:", peak)

    if peak["value"] > THRESHOLD:
        print("🚨 ALARM – vandstand over threshold")
    else:
        print("OK")


if __name__ == "__main__":
    main()
