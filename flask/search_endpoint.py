import os
import requests
from requests.auth import HTTPBasicAuth

# our demo filter that filters by geometry, date and cloud cover
from image_filters import filterClass


if __name__ == '__main__':
	search_function()

def search_function():
	# Search API request object
	search_endpoint_request = {
	  "item_types": ["PSScene4Band"],
	  "filter": filterClass.get_main_filter()
	}
	result = \
	  requests.post(
	    'https://api.planet.com/data/v1/quick-search',
	    auth=HTTPBasicAuth(os.environ['$PL_API_KEY'], ''),
	    json=search_endpoint_request)
	return result
