#####################################################################

# Example : perform high pass filterings in fourier space of image frame
# from a video file specified on the command line (e.g. python FILE.py
# video_file) or from an attached web camera

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2015 School of Engineering & Computing Science,
#                    Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

# version 0.1

#####################################################################

import cv2
import sys
import numpy as np
import math

#####################################################################

keep_processing = True;
camera_to_use = 1; # 0 if you have one camera, 1 or > 1 otherwise

#####################################################################

# create a simple high pass filter

def create_high_pass_filter(width, height, radius):
    hp_filter = np.ones((height, width, 2), np.float32);
    cv2.circle(hp_filter, (width / 2, height / 2), radius, (0,0,0), thickness=-1)
    return hp_filter

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
windowName2 = "Fourier Magnitude Spectrum"; # window name
windowName3 = "Filtered Image"; # window name

# if command line arguments are provided try to read video_name
# otherwise default to capture from attached H/W camera

if (((len(sys.argv) == 2) and (cap.open(str(sys.argv[1]))))
    or (cap.open(camera_to_use))):

    # create windows by name (as resizable)

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName2, cv2.WINDOW_NORMAL);
    cv2.namedWindow(windowName3, cv2.WINDOW_NORMAL);

    # add some track bar controllers for settings

    radius = 25;
    cv2.createTrackbar("radius", windowName2, radius, 200, nothing);

    # if video file successfully open then read frame from video

    if (cap.isOpened):
        ret, frame = cap.read();

    # convert to grayscale

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

    # use this single frame to set up optimized DFT settings

    hieght,width = gray_frame.shape;
    nheight = cv2.getOptimalDFTSize(hieght);
    nwidth = cv2.getOptimalDFTSize(width);

    while (keep_processing):

        # if video file successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read();

        # start a timer (to see how long processing and display takes)

        start_t = cv2.getTickCount();

         # convert to grayscale

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

        # Performance of DFT calculation, via the FFT, is better for array sizes of power of two.
        # Arrays whose size is a product of 2's, 3's, and 5's are also processed quite efficiently.
        # Hence ee modify the size of the array tothe optimal size (by padding zeros) before finding DFT.

        pad_right = nwidth - width;
        pad_bottom = nheight - hieght;
        nframe = cv2.copyMakeBorder(gray_frame,0,pad_bottom,0,pad_right,cv2.BORDER_CONSTANT, value = 0);

        # perform the DFT and get complex output

        dft = cv2.dft(np.float32(nframe),flags = cv2.DFT_COMPLEX_OUTPUT);

        # shift it so that we the zero-frequency, F(0,0), DC component to the center of the spectrum.

        dft_shifted = np.fft.fftshift(dft);

        # perform high pass filtering

        radius = cv2.getTrackbarPos("radius",windowName2);
        hp_filter = create_high_pass_filter(nwidth, nheight, radius);

        dft_filtered = cv2.mulSpectrums(dft_shifted, hp_filter, flags=0);

        # shift it back to original quaderant ordering

        dft = np.fft.fftshift(dft_filtered);

        # recover the original image via the inverse DFT

        filtered_img = cv2.dft(dft, flags = cv2.DFT_INVERSE);

        # normalized the filtered image into 0 -> 255 (8-bit grayscale) so we can see the output

        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(filtered_img[:,:,0]);
        filtered_img_normalized = filtered_img[:,:,0] * (1.0/(maxVal-minVal)) + ((-minVal)/(maxVal-minVal));
        filtered_img_normalized = np.uint8(filtered_img_normalized * 255);

        # calculate the magnitude spectrum and log transform + scale it for visualization

        magnitude_spectrum = np.log(cv2.magnitude(dft_filtered[:,:,0],dft_filtered[:,:,1]));

        # create a 8-bit image to put the magnitude spectrum into

        magnitude_spectrum_normalized = np.zeros((nheight,nwidth,1), np.uint8);

        # normalized the magnitude spectrum into 0 -> 255 (8-bit grayscale) so we can see the output

        cv2.normalize(np.uint8(magnitude_spectrum), magnitude_spectrum_normalized, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX);

        # display images

        cv2.imshow(windowName,gray_frame);
        cv2.imshow(windowName2,magnitude_spectrum_normalized);
        cv2.imshow(windowName3,filtered_img_normalized);

        # stop timer and convert to ms. (to see how long processing and display takes)

        stop_t = ((cv2.getTickCount() - start_t)/cv2.getTickFrequency()) * 1000;

        # start the event loop - essential

        # cv2.waitKey() is a keyboard binding function (argument is the time in milliseconds).
        # It waits for specified milliseconds for any keyboard event.
        # If you press any key in that time, the program continues.
        # If 0 is passed, it waits indefinitely for a key stroke.
        # (bitwise and with 0xFF to extract least significant byte of multi-byte response)

        # here we use a wait time in ms. that takes account of processing time already used in the loop

        key = cv2.waitKey(max(2, 40 - int(math.ceil(stop_t)))) & 0xFF; # wait 40ms (i.e. 1000ms / 25 fps = 40 ms)

        # It can also be set to detect specific key strokes by recording which key is pressed

        # e.g. if user presses "x" then exit

        if (key == ord('x')):
            keep_processing = False;

    # close all windows

    cv2.destroyAllWindows()

else:
    print("No video file specified or camera connected.")

#####################################################################


