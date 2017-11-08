# import the necessary packages
import numpy as np
import argparse
import cv2


#Run this line: python ocv.py --image lowres.png

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())

# load the image
image = cv2.resize(cv2.imread(args["image"]), (800,400))
im_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY);

# define the list of boundaries
boundaries = [([175], [255])]

# loop over the boundaries
for (lower, upper) in boundaries:
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	# find the colors within the specified boundaries and apply the mask
	mask = cv2.inRange(im_gray, lower, upper)
	im_mask = cv2.bitwise_and(im_gray, im_gray, mask = mask)

	thresh = 0;

	im_fill = cv2.threshold(im_mask, thresh, 255, cv2.THRESH_BINARY)[1];

	_,contour,hier = cv2.findContours(im_fill,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)

	for cnt in contour:
	    cv2.drawContours(im_fill,[cnt],0,255,-1)

	# show the images
	cv2.imshow("initial", image)
	cv2.imshow("images", np.vstack([im_gray, im_fill]))
	cv2.imwrite('contrasted.png', im_fill)
	cv2.waitKey(0)
