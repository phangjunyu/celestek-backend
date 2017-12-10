import sys,os
import requests
import urllib.request
import boto
import boto.s3
import json
import io
from tqdm import tqdm
# sys.path.append('/imageDownload')
from multiprocessing.dummy import Pool as ThreadPool
# from stats_endpoint import result_data
import stats_endpoint
# from search_endpoint import result
import search_endpoint
from retrying import retry
from requests.auth import HTTPBasicAuth
from boto.s3.key import Key
# from statistics import mean
# from operator import itemgetter
# import geopy.distance

if __name__ == '__main__':
	mainfunction()

# def generate_origin(coordinates):
# 	mean_long = mean(map(itemgetter(0), coordinates))
# 	mean_lat = mean(map(itemgetter(1), coordinates))
# 	return [mean_lat, mean_long]
#
#
# def estimate_longitude_distance(coordinates):
# 	min_long = min(map(itemgetter(0), coordinates))
# 	min_lat = min(map(itemgetter(1), coordinates))
# 	min_point = [min_lat, min_long]
# 	max_long = max(map(itemgetter(0), coordinates))
# 	max_lat = max(map(itemgetter(1), coordinates))
# 	max_point = [max_lat, max_long]
# 	geopy.distance.vincenty(min_point)

def mainfunction():
	with open('./config.json', 'r') as f:
	    config = json.load(f)
	#iterate over images collected for location by day collected and find the most recent date images were collected
	max_date = ''
	result_data = stats_endpoint.stats_function()
	for count_and_day_collected in result_data["buckets"]:
		day_collected = count_and_day_collected["start_time"]
		if day_collected > max_date:
			max_date = day_collected



	# parse max_date and re-concatenate date to compare to image_ids
	delim = '-'
	tokens = max_date.split(delim)
	date = tokens[0] + tokens[1] + tokens[2][:2]

	#find images that correspond to the most recent date and put them and their ids in lists
	search_endpoint_data = search_endpoint.search_function()
	images_to_download = []
	for feature in search_endpoint_data["features"]:
		if (feature["id"][:8] == date):
			coordinates = feature['geometry']['coordinates']
			image = {
				"id": feature["id"],
				"coordinates": coordinates
				# "origin": generate_origin(coordinates),
				# "width": generate_width_distance(coordinates),
			}
			images_to_download.append(image)

	# setup auth

	# "Wait 2^x * 1000 milliseconds between each retry, up to 10
	# seconds, then 10 seconds afterwards"

	#Use a ThreadPool to parallelize I/O bound operations
	parallelism = 5
	thread_pool = ThreadPool(parallelism)

	# All items will be sent to the `activate_item` function but only 5 will be running at once
	thread_pool.map(activate_item, images_to_download)

	AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
	AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

	conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
	bucket_name = config['AWS_BUCKET']
	bucket = conn.get_bucket(bucket_name)
	#bucket = conn.create_bucket(bucket_name,
	    #location=boto.s3.connection.Location.DEFAULT)

	# for image in tqdm(images_to_download):
	# 	item_id = image['id']
	# 	print(item_id)
	# 	download_and_upload_image(image, bucket)
	return images_to_download

@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)

def activate_item(image):
	item_id = image['id']
	print("attempting to activate: " + item_id)
	session = requests.Session()
	session.auth = (os.environ['$PL_API_KEY'], '')
	item_type = "PSScene4Band"
	asset_types = ["analytic", "analytic_xml"]
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

def download_and_upload_image(image, bucket):
	item_id = image['id']
	item_type = "PSScene4Band"
	asset_types = ["analytic", "analytic_xml"]
	for asset_type in asset_types:
		item_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, item_id)
		# Request a new download URL
		result = requests.get(item_url, auth=HTTPBasicAuth(os.environ['$PL_API_KEY'], ''))
		download_url = result.json()[asset_type]['location']
		if (asset_type == 'analytic') :
			output_file = item_id + '.tif'
		elif (asset_type == 'analytic_xml'):
			output_file = item_id + '.xml'
		#download
		file_object = urllib.request.urlopen(download_url)
		# processed_img = object_size.draw_boxes(file_object.read())
		# fp = io.BytesIO(processed_img)
		fp = io.BytesIO(file_object.read())
		#upload
		k = Key(bucket)
		k.key = output_file
		k.set_contents_from_file(fp)
		upload_image(file, k)
		url = k.generate_url(3600)
		image['link'] = url
		print(item_id,item_type, "uploaded")
