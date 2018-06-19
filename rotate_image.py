import math
import cv2
import numpy as np
from scipy import ndimage

def rotate_image():
    img_before = cv2.imread('ndvi_cmap.png')

    img_gray = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []

    for x1, y1, x2, y2 in lines[0]:
        cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    img_rotated = ndimage.rotate(img_before, median_angle)
    print("Angle is", median_angle)
    final_rotated = ndimage.rotate(img_rotated, 90)

    cv2.imwrite('rotated.jpg', final_rotated)

def largest_rotated_rect(w, h, angle):
    """
    Given a rectangle of size wxh that has been rotated by 'angle' (in
    radians), computes the width and height of the largest possible
    axis-aligned rectangle within the rotated rectangle.

    Original JS code by 'Andri' and Magnus Hoff from Stack Overflow

    Converted to Python by Aaron Snoswell
    """

    quadrant = int(math.floor(angle / (math.pi / 2))) & 3
    sign_alpha = angle if ((quadrant & 1) == 0) else math.pi - angle
    alpha = (sign_alpha % math.pi + math.pi) % math.pi

    bb_w = w * math.cos(alpha) + h * math.sin(alpha)
    bb_h = w * math.sin(alpha) + h * math.cos(alpha)

    gamma = math.atan2(bb_w, bb_w) if (w < h) else math.atan2(bb_w, bb_w)

    delta = math.pi - alpha - gamma

    length = h if (w < h) else w

    d = length * math.cos(alpha)
    a = d * math.sin(alpha) / math.sin(delta)

    y = a * math.cos(gamma)
    x = y * math.tan(gamma)

    return (
        bb_w - 2 * x,
        bb_h - 2 * y
    )


def crop_around_center():
    """
    Given a NumPy / OpenCV 2 image, crops it to the given width and height,
    around it's centre point
    """

    image_size = (image.shape[1], image.shape[0])
    image_center = (int(image_size[0] * 0.5), int(image_size[1] * 0.5))

    if(width > image_size[0]):
        width = image_size[0]

    if(height > image_size[1]):
        height = image_size[1]

    x1 = int(image_center[0] - 0)
    x2 = int(image_center[0] + 0)
    y1 = int(image_center[1] - 0)
    y2 = int(image_center[1] + 0)
    result = image[y1:y2, x1:x2]
    cv2.imwrite('final_image.png', result)
    return result

def remove_border():
    #https://stackoverflow.com/questions/13538748/crop-black-edges-with-opencv?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    """
    Given a NumPy / OpenCV 2 image, crops it to the given width and height,
    around it's centre point
    """
    img = cv2.imread('rotated.jpg')
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    COLOR_MIN = np.array([0, 0, 50],np.uint8)
    COLOR_MAX = np.array([255, 255, 255],np.uint8)
    frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
    imgray = frame_threshed
    ret,thresh = cv2.threshold(frame_threshed,0,255,0)
    _, contours, _= cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # Find the index of the largest contour
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt=contours[max_index]

    x,y,w,h = cv2.boundingRect(cnt)
    #cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
    result = img[y:y+h,x:x+w]
    cv2.imwrite('final_image.jpg', result)

if __name__ == "__main__":
    # rotate_image()
    remove_border()
