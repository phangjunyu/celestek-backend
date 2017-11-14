import os
import requests
from requests.auth import HTTPBasicAuth

# our demo filter that filters by geometry, date and cloud cover
from image_filters import sjc_golfcourse

# Stats API request object
stats_endpoint_request = {
  "interval": "day",
  "item_types": ["PSScene4Band"],
  "filter": sjc_golfcourse,
}

# fire off the POST request
result = \
  requests.post(
    'https://api.planet.com/data/v1/stats',
    auth=HTTPBasicAuth(os.environ['PL_API_KEY'], ''),
    json=stats_endpoint_request)

result_data = result.json()

