#####################################################################

# Example : live template matching via processing from a video file
# specified on the command line (e.g. python FILE.py video_file) or from an
# attached web camera

# N.B. use mouse to select region

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2015 Toby Breckon
#                    Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

# version 0.2

#####################################################################

import cv2
import sys
import math
import numpy as np

#####################################################################

keep_processing = True;
camera_to_use = 1; # 0 if you have one camera, 1 or > 1 otherwise

selection_in_progress = False; # support interactive region selection

#####################################################################

# select a region using the mouse

boxes = [];
current_mouse_position = np.ones(2, dtype=np.int32);

def on_mouse(event, x, y, flags, params):

    global boxes;
    global selection_in_progress;

    current_mouse_position[0] = x;
    current_mouse_position[1] = y;

    if event == cv2.EVENT_LBUTTONDOWN:
        boxes = [];
        # print 'Start Mouse Position: '+str(x)+', '+str(y)
        sbox = [x, y];
        selection_in_progress = True;
        boxes.append(sbox);

    elif event == cv2.EVENT_LBUTTONUP:
        # print 'End Mouse Position: '+str(x)+', '+str(y)
        ebox = [x, y];
        selection_in_progress = False;
        boxes.append(ebox);

#####################################################################

# define video capture object

cap = cv2.VideoCapture();

# define display window name

windowName = "Live Camera Input"; # window name
windowName2 = "Correlation Output"; # window name
windowNameSelection = "selected";

# if command line arguments are provided try to read video_name
# otherwise default to capture from attached H/W camera

if (((len(sys.argv) == 2) and (cap.open(str(sys.argv[1]))))
    or (cap.open(camera_to_use))):

    # create window by name (note flags for resizable or not)

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName2, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowNameSelection, cv2.WINDOW_NORMAL);

    # set a mouse callback

    cv2.setMouseCallback(windowName, on_mouse, 0);
    cropped = False;

    # usage

    print("USAGE: click and drag left to right to select an image region")

    while (keep_processing):

        # if video file successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read();

        # start a timer (to see how long processing and display takes)

        start_t = cv2.getTickCount();

        # select region using the mouse and display it

        if (len(boxes) > 1) and (boxes[0][1] < boxes[1][1]) and (boxes[0][0] < boxes[1][0]):
            crop = frame[boxes[0][1]:boxes[1][1],boxes[0][0]:boxes[1][0]].copy()
            boxes = [];
            h, w, c = crop.shape;   # size of template
            if (h > 0) and (w > 0):
                cropped = True;
                cv2.imshow(windowNameSelection,crop);

        # interactive display of selection box

        if (selection_in_progress):
            top_left = (boxes[0][0], boxes[0][1]);
            bottom_right = (current_mouse_position[0], current_mouse_position[1]);
            cv2.rectangle(frame,top_left, bottom_right, (0,255,0), 2);

        # if we have cropped a region perform template matching using
        # (normalized) cross correlation and draw rectangle around best match

        if cropped:
            correlation = cv2.matchTemplate(frame,crop,cv2.TM_CCOEFF_NORMED);
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(correlation);
            h, w, c = crop.shape;   # size of template
            top_left = max_loc;     # top left of where template matches image frame
            bottom_right = (top_left[0] + w, top_left[1] + h);
            cv2.rectangle(frame,top_left, bottom_right, (0,0,255), 2);

            cv2.imshow(windowName2,correlation);

        # display image

        cv2.imshow(windowName,frame);

        # stop the timer and convert to ms. (to see how long processing and display takes)

        stop_t = ((cv2.getTickCount() - start_t)/cv2.getTickFrequency()) * 1000;

        # start the event loop - essential

        # cv2.waitKey() is a keyboard binding function (argument is the time in milliseconds).
        # It waits for specified milliseconds for any keyboard event.
        # If you press any key in that time, the program continues.
        # If 0 is passed, it waits indefinitely for a key stroke.
        # (bitwise and with 0xFF to extract least significant byte of multi-byte response)
        # here we use a wait time in ms. that takes account of processing time already used in the loop

        # wait 40ms or less depending on processing time taken (i.e. 1000ms / 25 fps = 40 ms)

        key = cv2.waitKey(max(2, 40 - int(math.ceil(stop_t)))) & 0xFF;

        # It can also be set to detect specific key strokes by recording which key is pressed

        # e.g. if user presses "x" then exit

        if (key == ord('x')):
            keep_processing = False;

    # close all windows

    cv2.destroyAllWindows()

else:
    print("No video file specified or camera connected.")

#####################################################################


