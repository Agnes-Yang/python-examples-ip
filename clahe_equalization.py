#####################################################################

# Example : perform contrast limited histogram equalization (CLAHE) from a video file
# specified on the command line (e.g. python FILE.py video_file) or from an
# attached web camera

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2015 School of Engineering & Computing Science,
#                    Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

#####################################################################

import cv2
import numpy as np
import sys

#####################################################################

keep_processing = True;
camera_to_use = 1; # 0 if you have one camera, 1 or > 1 otherwise

#####################################################################

# basic grayscale histogram drawing in raw OpenCV using lines

# adapted from:
# https://raw.githubusercontent.com/Itseez/opencv/master/samples/python2/hist.py

def hist_lines(hist):
    h = np.ones((300,256,3)) * 255 # white background
    cv2.normalize(hist,hist,0,255,cv2.NORM_MINMAX)
    hist=np.int32(np.around(hist))
    for x,y in enumerate(hist):
        cv2.line(h,(x,0),(x,y),(0,0,0)) # black bars
    y = np.flipud(h)
    return y

#####################################################################

# this function is called as a call-back everytime the trackbar is moved
# (here we just do nothing)

def nothing(x):
    pass

#####################################################################

# define video capture object

cap = cv2.VideoCapture();

# define display window name

windowName1 = "Live Camera Input"; # window name
windowName2 = "Input Histogram"; # window name
windowName3 = "Processed Output"; # window name
windowName4 = "Output Histogram"; # window name

# if command line arguments are provided try to read video_name
# otherwise default to capture from attached H/W camera

if (((len(sys.argv) == 2) and (cap.open(str(sys.argv[1]))))
    or (cap.open(camera_to_use))):

    # create window by name (as resizable)

    cv2.namedWindow(windowName1, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName2, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName3, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName4, cv2.WINDOW_NORMAL);

    # add some track bar controllers for settings

    clip_limit = 2;
    cv2.createTrackbar("clip limit", windowName4, clip_limit, 25, nothing);
    tile_size = 8;
    cv2.createTrackbar("tile size", windowName4, tile_size, 64, nothing);

    while (keep_processing):

        # if video file successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read();

        # convert to grayscale

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

        # perform contrast limited adaptive equalization
        # based on example at:
        # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_histograms/py_histogram_equalization/py_histogram_equalization.html

        # get parameters from track bars

        clip_limit = cv2.getTrackbarPos("clip limit", windowName4);
        tile_size = cv2.getTrackbarPos("tile size", windowName4);

        # perform filtering

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size,tile_size)); # create filter
        output = clahe.apply(gray_img); # apply filter

        # display image

        cv2.imshow(windowName1,gray_img);
        cv2.imshow(windowName2,hist_lines(cv2.calcHist([gray_img],[0],None,[256],[0,256])));
        cv2.imshow(windowName3,output);
        cv2.imshow(windowName4,hist_lines(cv2.calcHist([output],[0],None,[256],[0,256])));

        # start the event loop - essential

        # cv2.waitKey() is a keyboard binding function (argument is the time in milliseconds).
        # It waits for specified milliseconds for any keyboard event.
        # If you press any key in that time, the program continues.
        # If 0 is passed, it waits indefinitely for a key stroke.
        # (bitwise and with 0xFF to extract least significant byte of multi-byte response)

        key = cv2.waitKey(40) & 0xFF; # wait 40ms (i.e. 1000ms / 25 fps = 40 ms)

        # It can also be set to detect specific key strokes by recording which key is pressed

        # e.g. if user presses "x" then exit

        if (key == ord('x')):
            keep_processing = False;

    # close all windows

    cv2.destroyAllWindows()

else:
    print("No video file specified or camera connected.")

#####################################################################


