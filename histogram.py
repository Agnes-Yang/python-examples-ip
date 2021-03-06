#####################################################################

# Example : calculate and display the grayscale histogram from a video file
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
camera_to_use = 0; # 0 if you have one camera, 1 or > 1 otherwise

#####################################################################

# basic grayscale histogram drawing in raw OpenCV using either a curve or lines

# adapted from:
# https://raw.githubusercontent.com/Itseez/opencv/master/samples/python2/hist.py

def hist_curve(hist):
    h = np.ones((300,256,3))  * 255 # white background
    bins = np.arange(256).reshape(256,1)
    cv2.normalize(hist,hist,0,255,cv2.NORM_MINMAX)
    hist=np.int32(np.around(hist))
    pts = np.int32(np.column_stack((bins,hist)))
    cv2.polylines(h,[pts],False,(0,0,0)) # black line
    y=np.flipud(h)
    return y

def hist_lines(hist):
    h = np.ones((300,256,3)) * 255 # white background
    cv2.normalize(hist,hist,0,255,cv2.NORM_MINMAX)
    hist=np.int32(np.around(hist))
    for x,y in enumerate(hist):
        cv2.line(h,(x,0),(x,y),(0,0,0)) # black bars
    y = np.flipud(h)
    return y

#####################################################################

# define video capture object

cap = cv2.VideoCapture();

# define display window name

windowName = "Live Camera Input (as Greyscale)"; # window name
windowName2 = "Histogram (bar graph)"; # window name
windowName3 = "Histogram (line graph)"; # window name


# if command line arguments are provided try to read video_name
# otherwise default to capture from attached H/W camera

if (((len(sys.argv) == 2) and (cap.open(str(sys.argv[1]))))
    or (cap.open(camera_to_use))):

    # create window by name (as resizable)

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName2, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName3, cv2.WINDOW_NORMAL);

    while (keep_processing):

        # if video file successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read();

        # convert to grayscale

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

        # calculate the histogram over the whole image, for 1 channel
        # with one bin (histogram entry) for each value in the range 0 -> 255

        hist = cv2.calcHist([gray_img],[0],None,[256],[0,256]);

        # draw the histogram distribution as an image
        # in two different visual forms (same info.)

        hist_img = hist_lines(hist);
        hist_img2 = hist_curve(hist);

        # display images

        cv2.imshow(windowName,gray_img);
        cv2.imshow(windowName2,hist_img);
        cv2.imshow(windowName3,hist_img2);

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
