#####################################################################

# Example : JPEG compression as processing on frames from a video file
# specified on the command line (e.g. python FILE.py video_file) or from an
# attached web camera

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2015 Toby Breckon
#                    Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

#####################################################################

import cv2
import sys
import math

#####################################################################

keep_processing = True;
camera_to_use = 1; # 0 if you have one camera, 1 or > 1 otherwise

#####################################################################

# this function is called as a call-back everytime the trackbar is moved
# (here we just do nothing)

def nothing(x):
    pass

#####################################################################

# define video capture object

cap = cv2.VideoCapture();

# define display window name

windowName = "Live Camera Input"; # window name
windowName2 = "JPEG compression noise"; # window name
windowNameJPEG = "JPEG compressed version"; # window name

# if command line arguments are provided try to read video_name
# otherwise default to capture from attached H/W camera

if (((len(sys.argv) == 2) and (cap.open(str(sys.argv[1]))))
    or (cap.open(camera_to_use))):

    # create window by name (note flags for resizable or not)

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName2, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowNameJPEG, cv2.WINDOW_NORMAL);

    jpeg_quality = 90;
    cv2.createTrackbar("JPEG quality", windowName2, jpeg_quality, 100, nothing);

    amplification = 0;
    cv2.createTrackbar("amplification", windowName2, amplification, 255, nothing);

    while (keep_processing):

        # if video file successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read();

        # start a timer (to see how long processing and display takes)

        start_t = cv2.getTickCount();

        # write/compress and then read back from as JPEG

        jpeg_quality = cv2.getTrackbarPos("JPEG quality",windowName2);
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),jpeg_quality];

        # either via file output / input

        # cv2.imwrite("camera.jpg", frame, encode_param);
        # jpeg_img = cv2.imread("camera.jpg");

        # or via encoding / decoding in a memory buffer

        retval, buffer = cv2.imencode(".JPG", frame, encode_param);
        jpeg_img = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR);

        # compute absolute difference between original and compressed version

        diff_img = cv2.absdiff(jpeg_img, frame);

        # retrieve the amplification setting from the track bar

        amplification = cv2.getTrackbarPos("amplification",windowName2);

        # multiple the result to increase the amplification (so we can see small pixel changes)

        amplified_diff_img = diff_img * amplification;

        # display images

        cv2.imshow(windowName,frame);
        cv2.imshow(windowName2, amplified_diff_img);
        cv2.imshow(windowNameJPEG, jpeg_img);


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


