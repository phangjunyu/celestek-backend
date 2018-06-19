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
import os
import math
from lxml import etree
import requests

NUM_HEIGHT = 11
NUM_WIDTH = 12

XML_TAG = '{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}epsgCode'
XML_COORD_TAGS = [
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topRight',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomRight',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomLeft'

]

path = "C:\\Users\\phangjunyu\\Desktop\\spaceview\\Backend\\image_slices"
XML_ARG = "C:\\Users\\phangjunyu\\Desktop\\spaceview\\Backend\\20180312_181743_101e.xml"
LB_ARG = 195
UB_ARG = 255
#load the xml
xml_coordinates = []
for _,v in etree.iterparse(XML_ARG):
	if v.tag in XML_COORD_TAGS:
		lat = float(v.find('{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}latitude').text)
		long = float(v.find('{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}longitude').text)
		xml_coordinates.append((lat, long))

if __name__ == '__main__':
	mainfunction()

def mainfunction(startandend=None):
	# there should be 50 images? 10 length cuts and 5 breadth cuts
	topLeft = xml_coordinates[0]
	height = abs(xml_coordinates[0][0]-xml_coordinates[3][0])
	width = abs(xml_coordinates[0][1]-xml_coordinates[1][1])
	transformed_boxes = []
	#TODO: CHANGE THIS
	for index, image_slice in enumerate(os.listdir(path)):
		# load the image, convert it to grayscale, and blur it slightly
		# Also defines pixel coordinate limits of image 900 for x and 350 for y
		# image = cv2.resize(cv2.imread(image_slice), (IMAGE_WIDTH, IMAGE_HEIGHT))
		image = cv2.imread(path+"\\"+image_slice)
		IMAGE_HEIGHT, IMAGE_WIDTH = image.shape[0:2]

		im_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

		# create NumPy arrays from the boundaries
		lower = np.array(LB_ARG, dtype = "uint8")
		upper = np.array(UB_ARG, dtype = "uint8")

		# find the colors within the specified boundaries and apply the mask
		mask = cv2.inRange(im_gray, lower, upper)
		im_mask = cv2.bitwise_and(im_gray, im_gray, mask = mask)

		thresh = 0;

		im_fill = cv2.threshold(im_mask, thresh, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1];

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
		if len(cnts) == 0:
			continue
		(cnts, _) = contours.sort_contours(cnts)

		width_ = width/NUM_WIDTH
		height_ = height/NUM_HEIGHT

		# loop over the contours individually
		final_boxes = []
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
			final_box = []
			(tl, tr, br, bl) = box
			h = int(index/NUM_HEIGHT)
			w = index%NUM_WIDTH
			for coordinate in box:
				final_coordinate = (topLeft[0] - ((height_ * h) + coordinate[1]/IMAGE_HEIGHT*height_), topLeft[1] + ((width_ * w) + coordinate[0]/IMAGE_WIDTH*width_))

				final_box.append(final_coordinate)

			#TODO: if box outside of bounding range filter out?
			final_boxes.append(final_box)

		for box in final_boxes:
			transformed_box = []
			for point in box:
				# tb = pyproj.transform(p2, p1, point[0], point[1])
				tb = [point[0].tolist(), point[1].tolist()]
				transformed_box.append({'lat': tb[0], 'lng': tb[1]})
			transformed_boxes.append(transformed_box)

	return {'final_boxes': transformed_boxes}
