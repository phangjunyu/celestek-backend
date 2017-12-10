# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

if __name__ == "__main__":
	draw_boxes(image,coordinates)

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def draw_boxes(image,coordinates):
	# construct the argument parse and parse the arguments
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-i", "--image", required=True)
	# args = vars(ap.parse_args())
    #
	# # load the image, convert it to grayscale, and blur it slightly
	# image = cv2.imread(args["image"])

	#Get Image
	from PIL import Image
	with Image.open(image) as img:
	        width, height = img.size
	print('Image width = ' + str(width) + ' | Image height = ' + str(height))

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (7, 7), 0)

	# perform edge detection, then perform a dilation + erosion to
	# close gaps in between object edges
	edged = cv2.Canny(gray, 50, 100)
	edged = cv2.dilate(edged, None, iterations=1)
	edged = cv2.erode(edged, None, iterations=1)

	# find contours in the edge map
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# sort the contours from left-to-right and initialize the
	# 'pixels per metric' calibration variable
	(cnts, _) = contours.sort_contours(cnts)
	pixelsPerMetric = None

	#Convert box points into longitude/latitude given array (use import later)
	# dummy_coord = [
	#         [
	#           -122.04540252685548,
	#           39.630151307924194
	#         ],
	#         [
	#           -122.04591751098631,
	#           39.61640012616186
	#         ],
	#         [
	#           -122.11166381835936,
	#           39.589947866228904
	#         ],
	#         [
	#           -122.09793090820311,
	#           39.583730118967985
	#         ],
	#         [
	#           -122.07956314086915,
	#           39.582936323839206
	#         ],
	#         [
	#           -122.02136993408203,
	#           39.58240712203527
	#         ],
	#         [
	#           -121.98806762695311,
	#           39.6206315500488
	#         ],
	#         [
	#           -121.99304580688477,
	#           39.630151307924194
	#         ],
	#         [
	#           -122.04540252685548,
	#           39.630151307924194
	#         ] ]

	#Find the bottom-left most corner in long/lat of the image
	#Find coordinate with least x, then highest y
	min_lat = min([float(i[1]) for i in dummy_coord])
	min_long = min([float(i[0]) for i in dummy_coord if i[1] == min_lat])
	max_long = min([float(i[0]) for i in dummy_coord])
	print([min_lat, min_long])

	orig = image.copy()
	# loop over the contours individually
	for c in cnts:
		# if the contour is not sufficiently large, ignore it
		if cv2.contourArea(c) < 100:
			continue

		# compute the rotated bounding box of the contour
		box = cv2.minAreaRect(c)
		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")

		# order the points in the contour such that they appear
		# in top-left, top-right, bottom-right, and bottom-left
		# order, then draw the outline of the rotated bounding
		# box
		box = perspective.order_points(box)
		cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

		# loop over the original points and draw them
		for (x, y) in box:
			cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

		# unpack the ordered bounding box, then compute the midpoint
		# between the top-left and top-right coordinates, followed by
		# the midpoint between bottom-left and bottom-right coordinates
		(tl, tr, br, bl) = box
		(tltrX, tltrY) = midpoint(tl, tr)
		(blbrX, blbrY) = midpoint(bl, br)
		print ('Box pixel coordinates: ' + str(tl) + str(tr) + str(bl) + str(br))

		# compute the midpoint between the top-left and top-right points,
		# followed by the midpoint between the top-right and bottom-right
		(tlblX, tlblY) = midpoint(tl, bl)
		(trbrX, trbrY) = midpoint(tr, br)

		#Convert from box coordinates to lat/long
	    #bl
		lat_diff = bl[1] - 0
		latcoord = min_lat + lat_diff*abs((max_long-min_long)/(tl[1]-bl[1]))

		long_diff = (-1)* (bl[0] - height)
		longcoord = min_long + long_diff*abs((max_long-min_long)/(tl[1]-bl[1]))
		print ('bl lat/long coordinates: ' + str(latcoord) + ', ' +str(longcoord))
		bl = [latcoord, longcoord]

		#br
		lat_diff = (br[1] - 0)
		latcoord = min_lat + lat_diff*abs((max_long-min_long)/(tl[1]-bl[1]))

		long_diff = (-1)* (br[0] - height)
		longcoord = min_long + long_diff*abs((max_long-min_long)/(tl[1]-bl[1]))
		print ('br lat/long coordinates: ' + str(latcoord) + ', ' + str(longcoord))
		br = [latcoord, longcoord]

		#tl
		lat_diff = (tl[1] - 0)
		latcoord = min_lat + lat_diff*abs((max_long-min_long)/(tl[1]-bl[1]))

		long_diff = (-1)* (tl[0] - height)
		longcoord = min_long + long_diff*abs((max_long-min_long)/(tl[1]-bl[1]))
		print ('tl lat/long coordinates: ' + str(latcoord) + ', ' +str(longcoord))
		tl = [latcoord, longcoord]

		#tr
		lat_diff = (tr[1] - 0)
		latcoord = min_lat + lat_diff*abs((max_long-min_long)/(tl[1]-bl[1]))

		long_diff = (-1)* (tr[0] - height)
		longcoord = min_long + long_diff*abs((max_long-min_long)/(tl[1]-bl[1]))
		print ('tr lat/long coordinates: ' + str(latcoord) + ', ' +str(longcoord))
		tr = [latcoord, longcoord]

		# exec(open("./elevationavg.py").read())

		# draw the midpoints on the image
		cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

		# draw lines between the midpoints
		cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
			(255, 0, 255), 2)
		cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
			(255, 0, 255), 2)

		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
		dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

		# if the pixels per metric has not been initialized, then
		# compute it as the ratio of pixels to supplied metric
		# (in this case, inches)
		if pixelsPerMetric is None:
			pixelsPerMetric = dB / (width/((bl[0]-br[0])*(10000000/90)))

		# compute the size of the object
		dimA = dA / pixelsPerMetric
		dimB = dB / pixelsPerMetric
		if (dimA < 0.2 and dimB < 0.2):
			continue

		# draw the object sizes on the image
		cv2.putText(orig, "{:.1f}nm".format(dimA),
			(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (255, 255, 255), 2)
		cv2.putText(orig, "{:.1f}nm".format(dimB),
			(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (255, 255, 255), 2)

	# show the output image
	# cv2.imshow("Image", orig)
	# cv2.waitKey(0)
	return orig
