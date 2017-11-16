import boto3
import requests
import json

with open('config.json', 'r') as f:
    config = json.load(f)

# Get the service client.
s3 = boto3.client('s3',
					aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
    				aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'])

# Generate the URL to get 'key-name' from 'bucket-name'
url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': config['AWS_BUCKET'],
        'Key': 'test'
    }
)

# Use the URL to perform the GET operation. You can use any method you like
# to send the GET, but we will use requests here to keep things simple.
response = requests.get(url, stream=True)
with open('pic1.jpg', 'wb') as handle:
	if not response.ok:
		print(response)

	for block in response.iter_content(1024):
		if not block:
			break
		handle.write(block)
