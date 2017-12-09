import os
import requests
from requests.auth import HTTPBasicAuth
# our demo filter that filters by geometry, date and cloud cover
from image_filters import filterClass

if __name__ == '__main__':
	stats_function()

def stats_function():
	# Stats API request object
	stats_endpoint_request = {
	  "interval": "day",
	  "item_types": ["PSScene4Band"],
	  "filter": filterClass.get_main_filter()
	}
	# fire off the POST request
	result = \
	  requests.post(
	    'https://api.planet.com/data/v1/stats',
	    auth=HTTPBasicAuth(os.environ['$PL_API_KEY'], ''),
	    json=stats_endpoint_request)

	result_data = result.json()
	print(result_data)
	return result_data
