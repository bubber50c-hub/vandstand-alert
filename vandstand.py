import os
import requests
import json

API_KEY = os.environ["API_KEY"]

url = "https://dmigw.govcloud.dk/v1/forecastedr/collections/ocean_forecast/items"

params = {
    "api-key": API_KEY,
    "limit": 1
}

r = requests.get(url, params=params)

print("STATUS:", r.status_code)
print("RAW RESPONSE:")
print(json.dumps(r.json(), indent=2))
