import os
import requests
import pycurl
import urllib.request
import boto
import boto.s3
import json
import io
from multiprocessing.dummy import Pool as ThreadPool
from stats_endpoint import result_data
from search_endpoint import result
from retrying import retry
from osgeo import gdal
from requests.auth import HTTPBasicAuth
from boto.s3.key import Key

with open('../config.json', 'r') as f:
    config = json.load(f)

#iterate over images collected for location by day collected and find the most recent date images were collected
max_date = ''
for count_and_day_collected in result_data["buckets"]:
	day_collected = count_and_day_collected["start_time"]
	if day_collected > max_date:
		max_date = day_collected

#parse max_date and re-concatenate date to compare to image_ids
delim = '-'
tokens = max_date.split(delim)
date = tokens[0] + tokens[1] + tokens[2][:2]

#find images that correspond to the most recent date and put them and their ids in lists
search_endpoint_data = result.json()
images_to_download = []
image_ids_to_download = []
for feature in search_endpoint_data["features"]:
	if (feature["id"][:8] == date):
		images_to_download.append(feature) #probably do not need
		image_ids_to_download.append(feature["id"])


item_type = "PSScene4Band"
asset_types = ["analytic", "analytic_xml"]

# setup auth
session = requests.Session()
session.auth = (os.environ['PL_API_KEY'], '')

# "Wait 2^x * 1000 milliseconds between each retry, up to 10
# seconds, then 10 seconds afterwards"
@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def activate_item(item_id):
	print("attempting to activate: " + item_id)
	
	# request an item
	item = \
	  session.get(
	    ("https://api.planet.com/data/v1/item-types/" +
	    "{}/items/{}/assets/").format(item_type, item_id))

	# raise an exception to trigger the retry
	if item.status_code == 429:
		raise Exception("rate limit error")

	# request activation
	for asset_type in asset_types : 
		# extract the activation url from the item for the desired asset
		item_activation_url = item.json()[asset_type]["_links"]["activate"]
		# request activation
		response = session.post(item_activation_url)

		if response.status_code == 429:
			raise Exception("rate limit error")
		print("activation succeeeded for item " + item_id)

#Use a ThreadPool to parallelize I/O bound operations
parallelism = 5
thread_pool = ThreadPool(parallelism)

# All items will be sent to the `activate_item` function but only 5 will be running at once
thread_pool.map(activate_item, image_ids_to_download)

AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket_name = config['AWS_BUCKET']
#bucket = conn.create_bucket(bucket_name,
    #location=boto.s3.connection.Location.DEFAULT)

def download_and_upload_image(item_id):
	for asset_type in asset_types:
		item_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, item_id)
		# Request a new download URL
		result = requests.get(item_url, auth=HTTPBasicAuth(os.environ['PL_API_KEY'], ''))
		download_url = result.json()[asset_type]['location']
		if (asset_type == 'analytic') :
			output_file = item_id + '_tif'
		elif (asset_type == 'analytic_xml'):
			output_file = item_id + '_xml'
		#urllib.request.urlretrieve(download_url, output_file)
		bucket = conn.get_bucket(bucket_name)
		k = Key(bucket)
		k.key = output_file
		file_object = urllib.request.urlopen(download_url)
		fp = io.BytesIO(file_object.read())
		k.set_contents_from_file(fp)     

for item_id in image_ids_to_download:
	print(item_id)
	download_and_upload_image(item_id)

