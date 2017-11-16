import os
import requests
from requests.auth import HTTPBasicAuth

# our demo filter that filters by geometry, date and cloud cover
from image_filters import sjc_golfcourse

# Search API request object
search_endpoint_request = {
  "item_types": ["PSScene4Band"],
  "filter": sjc_golfcourse
}

result = \
  requests.post(
    'https://api.planet.com/data/v1/quick-search',
    auth=HTTPBasicAuth(os.environ['PL_API_KEY'], ''),
    json=search_endpoint_request)
