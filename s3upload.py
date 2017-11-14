import boto
import boto.s3
import sys
import json
from boto.s3.key import Key

with open('config.json', 'r') as f:
    config = json.load(f)


bucket_name = config.AWS_ACCESS_KEY_ID.lower() + 'space-view'
conn = boto.connect_s3(config.AWS_ACCESS_KEY_ID,
        config.AWS_SECRET_ACCESS_KEY)


bucket = conn.create_bucket(bucket_name,
    location=boto.s3.connection.Location.DEFAULT)

testfile = "test.png"
print('Uploading %s to Amazon S3 bucket %s' %(testfile, bucket_name))

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


k = Key(bucket)
k.key = 'test'
k.set_contents_from_filename(testfile,
    cb=percent_cb, num_cb=10)
