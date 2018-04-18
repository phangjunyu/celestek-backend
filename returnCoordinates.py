# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import shapely.geometry
import pyproj
from lxml import etree

IMAGE_WIDTH = 900
IMAGE_HEIGHT = 350
XML_TAG = '{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}epsgCode'
XML_COORD_TAGS = [
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topRight',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomRight'
]

# python sv.py --image joined.jpg --xml original_xml.xml --width 0.995 --lb 190 --ub 255

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-x", "--xml", required=True,
	help="path to the xml file")
ap.add_argument("-w", "--width", type=float, required=True,
	help="width of the left-most object in the image (in inches)")
ap.add_argument("-lb", "--lb", type=float, required=True,
	help="lower limit of pixel color from 0 - 255")
ap.add_argument("-ub", "--ub", type=float, required=True,
	help="upper limit of pixel color from 0 - 255")
args = vars(ap.parse_args())


#load the xml
xml_coordinates = []
for _,v in etree.iterparse(args["xml"]):
	if v.tag in x:
        lat = float(v.find('{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}latitude').text)
        long = float(v.find('{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}longitude').text)
        xml_coordinates.append((lat, long))
    elif v.tag == XML_TAG:
        current_epsg = "epsg:"+v.text


# load the image, convert it to grayscale, and blur it slightly
# Also defines pixel coordinate limits of image 900 for x and 350 for y
image = cv2.resize(cv2.imread(args["image"]), (IMAGE_WIDTH, IMAGE_HEIGHT))

im_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

# create NumPy arrays from the boundaries
lower = np.array(args["lb"], dtype = "uint8")
upper = np.array(args["ub"], dtype = "uint8")

# find the colors within the specified boundaries and apply the mask
mask = cv2.inRange(im_gray, lower, upper)
im_mask = cv2.bitwise_and(im_gray, im_gray, mask = mask)

thresh = 0;

im_fill = cv2.threshold(im_mask, thresh, 255, cv2.THRESH_BINARY)[1];

_,contour,hier = cv2.findContours(im_fill,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)

for cnt in contour:
    cv2.drawContours(im_fill,[cnt],0,255,-1)

gray = cv2.GaussianBlur(im_fill, (7, 7), 0)

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
# original = cv2.imread("original.tif"

#set the projection types
p1 = pyproj.Proj(init=current_epsg)
# 3857 is metric system
p2 = pyproj.Proj(init="epsg:3857")
transformed_coordinates = []
#use only NW and SE coords
for i in range(len(xml_coordinates)):
	transformed_coordinates.append(pyproj.transform(p1, p2, xml_coordinates[i][0], xml_coordinates[i][1]))

# loop over the contours individually
for c in cnts:
	# if the contour is not sufficiently large, ignore it
	if cv2.contourArea(c) < 1000:
		continue

	# compute the rotated bounding box of the contour
	orig = image.copy()
	box = cv2.minAreaRect(c)
	box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
	box = np.array(box, dtype="int")

	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
	box = perspective.order_points(box)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
	(tl, tr, br, bl) = box

	(tltrX, tltrY) = midpoint(tl, tr)
	(blbrX, blbrY) = midpoint(bl, br)

	# compute the midpoint between the top-left and top-right points,
	# followed by the midpoint between the top-righ and bottom-right
	(tlblX, tlblY) = midpoint(tl, bl)
	(trbrX, trbrY) = midpoint(tr, br)

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
