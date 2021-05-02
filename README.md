

# Pupillary distance measurement
This repo aims to measure real pupilary distance using a megnetic card. To do the measurement, place a standard magnetic card facing the camera on your forehead with the longer edge parallel to the line connecting your eyes. Try to make sure the lower edge is on the same vertical plane that your eyes on. You can either take a photo on your own or use web camera by `python web_camera_capture.py`. Press space to take a photo. 

## Dependencies
OpenCV is required. Run `pip install opencv-python`.

## Usage
`python pupil_dist_measure.py -i path/to/image [-d auto/manual]`. Default detection method is manual.

### Manual detection
We need to manually click 4 points in the following order in order to do the calculation: bottom left corner of the magnetic card, right bottom of the magnetic card, center of left pupil (left on the image), center of right pupil (right on the image). Card width on image, pupillary distance on image, and real pupillary distance will be printed out on terminal.
 - Press 'r' to reselect all points.

### Auto detection
Currently, auto detection couldn't work well on card dection, so only pupillary distance on image will be measured and printed out on terminal. The detected eye center will be drawn on output image `detection` saved in the same folder.

## Features
The main idea is to measure the pupilary distance on the image, then use the relative scale calculated using card width on the image and real length 8.56cm to find real pupilary distance. The challenge is on accurate pupil center detection and card detection. The manual detection is more accurate with error <=2mm. Auto detection, however, doesn't work well on card detection, so for now it can only measure pupilary distance on the image. To improve the pupil center detection, I made some adjustments on Lisa and Sharon's code: 
- To find the pupil center, Instead of using the center of the contour with largest area found in eye area, try to find the min enclosing circle of the contour first using `cv2.minEnclosingCircle`, then use the center of the min enclosing center. 
- To find contours in eye area, we used to first binary the pixels by a fixed threshold using `cv2.threshold`. It doesn't work well for all cases. Therefore, I try 4 different threshold values (20, 30, 40, 50) and pick the one which produces the largest fraction of largest-area contour area over its min enclosing circle area.

## Reference
- `web_camera_capture` adapted from [https://stackoverflow.com/questions/34588464/python-how-to-capture-image-from-webcam-on-click-using-opencv](https://stackoverflow.com/questions/34588464/python-how-to-capture-image-from-webcam-on-click-using-opencv).
- Pupil auto detection developed based on Lisa and Sharon's code in [https://github.com/vision-correcting-display/VCD-3D/blob/master/eye_tracking/eyes_captured.py](https://github.com/vision-correcting-display/VCD-3D/blob/master/eye_tracking/eyes_captured.py). 


