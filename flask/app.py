from flask import Flask, request, make_response, jsonify, Response
from datetime import datetime, timedelta
from time import strftime
import json
import ast


app = Flask(__name__)

def generate_date():
	current_date = datetime.today()
	month_ago = current_date - timedelta(days = 30)
	current_date = current_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
	month_ago = month_ago.strftime("%Y-%m-%dT%H:%M:%S.000Z")
	return current_date, month_ago


@app.route("/")
def hello():
    return "Hello SpaceView!"


@app.route('/test/', methods=['GET', 'POST'])
def downloadAndUploadImagesToS3():
    if request.method == 'POST':
	    return make_response("POST SPACEVIEW", 200)
    else:
	    return make_response("GET SPACEVIEW", 200)

@app.route('/returnCoordinates', methods=['GET'])
def getCoordinates():
	# s = request.form.get('startpoint')
	# e = request.form.get('startpoint')
	# startandend = None
	# if not (s == "" and e == ""):
	# 	startpoint = ast.literal_eval(s)
	# 	endpoint = ast.literal_eval(e)
	# 	start = {"lat": startpoint[0], "lng": startpoint[1]}
	# 	end = {"lat": endpoint[0], "lng": endpoint[1]}
	# 	startandend = [start, end]
	import returnCoordinates
	json_boxes = json.dumps(returnCoordinates.mainfunction(None))
	return json_boxes

@app.route('/getImageURLs/', methods=['POST'])
def superfunction():

	data = request.get_json()
	coordinates = data['nameValuePairs']['coordinates']
	for i, point in enumerate(coordinates):
		coordinates[i] = list(reversed(coordinates[i]))
	current_date, month_ago = generate_date()
	from image_filters import filterClass
	filterClass.set_date_range_filter(current_date, month_ago)
	filterClass.set_geo_json_geometry(coordinates)
	filterClass.set_geometry_filter()
	filterClass.set_main_filter()
	import get_images
	images = get_images.mainfunction()
	print(images)
	json_images = Response(json.dumps(images),  mimetype='application/json')
	return make_response(json_images,200)


if __name__ == '__main__':
    app.run(debug=True)
