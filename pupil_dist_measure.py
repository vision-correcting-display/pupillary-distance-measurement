# import the necessary packages
import argparse
import cv2
from matplotlib import pyplot as plt
from imutils import paths
import numpy as np
import imutils
import math
import sys

# FOR MANUAL DETECTION
# refPt stores 4 points for card width and pupillary distance respectively.
refPt = []
card_width = 0
pupillary_dist = 0


def dist(pt1, pt2):
    return pow(pow(pt1[0]-pt2[0],2)+pow(pt1[1]-pt2[1],2), 0.5)


def click_and_measure(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, card_width, pupillary_dist
    # if the left mouse button was clicked, record the point
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt.append((x, y))
        # draw the point clicked on the image
        cv2.circle(image, refPt[-1], 5, (255, 255, 255), 3)
        cv2.imshow("image", image)
        # if 2 points clicked, calculate the card width on image
        if len(refPt) == 2:
            cv2.line(image, refPt[0], refPt[1], (0, 0, 255), 2)
            card_width = dist(refPt[0], refPt[1])
            print("card width on image (pixel): ", card_width)
        # if 4 points clicked, calculate the pupillary distance on image and real pupillary distance.
        elif len(refPt) == 4:
            cv2.line(image, refPt[2], refPt[3], (0, 0, 255), 2)
            pupillary_dist = dist(refPt[2], refPt[3])
            real_pupillary_dist = pupillary_dist * 8.56 / card_width
            print("pupillary distance on image (pixel): ", pupillary_dist)
            print("pupillary distance: ", real_pupillary_dist)


# FOR AUTO DETECTION
def auto_measure(frame, eyes_cascade):
    # Simplify the image (color isn't really necessary)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # graphical rep of the gray picture
    frame_gray = cv2.equalizeHist(frame_gray)
    height, width, _ = frame.shape

    # instantiations
    left_eye = None
    right_eye = None
    pupilliary_distance = 0

    h = height
    w = width
    x = 0
    y = 0
    # -- In each face, detect eyes
    eyes = eyes_cascade.detectMultiScale(frame_gray)
    for (ex, ey, ew, eh) in eyes:
        # filtering potential false eyes (mouth and nose)
        if ey + eh < int(2 * h / 3) and ew > 100 and eh > 100:
            # create eye region
            eyeROI = frame[ey + y:ey + eh + y, ex + x:ex + ew + x]
            eyeROI_center = (x + ex + ew // 2, y + ey + eh // 2)
            radius = int(round((ew + eh) * 0.25))
            # eye drawing
            cv2.circle(frame, eyeROI_center, radius, (255, 0, 0), 4)
            x_pos, y_pos = get_iris_region(eyeROI, x, y, ex, ey, frame)
            if x_pos < x + (w // 2) and x_pos != -1:
                left_eye = (x_pos, y_pos)
            elif x_pos != -1:
                right_eye = (x_pos, y_pos)

            if left_eye is not None and right_eye is not None:
                pupilliary_distance = dist(left_eye, right_eye)
                cv2.line(frame, left_eye, right_eye, (0, 0, 255), 2)
                break
    plt.imshow(frame)
    plt.savefig('detection.jpg', dpi=300)
    return pupilliary_distance


def get_iris_region(eyeROI, face_x, face_y, eye_x, eye_y, frame):
    grayEye = cv2.cvtColor(eyeROI, cv2.COLOR_BGR2GRAY)
    grayEye = cv2.GaussianBlur(grayEye, (7, 7), 0)
    max_frac = 0
    max_cnt = 0
    max_circle_center = (0, 0)
    max_circle_radius = int(0)
    for thres in [20,30,40,50]:
        _, threshold = cv2.threshold(grayEye, thres, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

        for cnt in contours:
            (x, y, w, h) = cv2.boundingRect(cnt)
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            frac = cv2.contourArea(cnt) / (radius * radius * math.pi)
            if frac > max_frac:
                max_frac = frac
                max_cnt = cnt
                max_circle_center = (int(x), int(y))
                max_circle_radius = int(radius)
            break

    cv2.drawContours(eyeROI, [max_cnt], -1, (255, 0, 0), 3)
    cv2.circle(eyeROI, max_circle_center, max_circle_radius, (0, 255, 0), 2)

    x_pos = max_circle_center[0] + face_x + eye_x
    y_pos = max_circle_center[1] + face_y + eye_y
    cv2.circle(frame, (x_pos, y_pos), 5, (255, 255, 255), 3)
    return x_pos, y_pos


def find_eye_dist(eye_img):
    # Defining Haar Cascade classifier (eyes and face)
    eyes_cascade_name = 'haarcascade_eye.xml'
    eyes_cascade = cv2.CascadeClassifier()
    # -- 1. Load the cascade
    if not eyes_cascade.load(cv2.samples.findFile(eyes_cascade_name)):
        print('--(!)Error loading eyes cascade')
        exit(0)
    eye_dist = auto_measure(eye_img, eyes_cascade)
    if eye_dist == 0:
        sys.exit("Eyes not detected. Please retake the photo!")
    print("pupillary distance on image (pixel): ", eye_dist)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
ap.add_argument("-d", "--detection", default="manual",
                help="optional, choose auto detection (auto) or manual detection (manual) (default)")
args = vars(ap.parse_args())
# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
if args["detection"] == "manual":
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_measure)
    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        # if the 'r' key is pressed, reset the point selection
        if key == ord("r"):
            image = clone.copy()
        # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            break
    # close all open windows
    cv2.destroyAllWindows()
elif args["detection"] == "auto":
    find_eye_dist(image)
else:
    sys.exit("Please pick detection method from 'auto' and 'manual'.")
