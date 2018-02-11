#!/usr/bin/env python

# import the necessary packages
from imutils.video import VideoStream
from collections import deque
from classes.motors import Motors
from classes.servo import Servo
import datetime
import argparse
import imutils
import time
import cv2
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=-1, help="whether or not the Raspberry Pi camera should be used")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())
 
# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(1.0)

greenLower = (21, 100, 50)
greenUpper = (41, 255, 255)

pts = deque(maxlen=args["buffer"])

width = 400
height = 300

# Turn on motors
motors = Motors()
motors.toggleMotors("on")

# Servo
servo = Servo()
servoDutyCycle = 7.5;

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=width)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 7:
			# draw the circle and centroid on the frame,
			cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

			# write center coords on the screen
			text = "Height: " + str(frame.shape[0]) + " Width: " + str(frame.shape[1])
			text += " X: " +  str(int(x)) + " Y: " + str(int(y))

			direction = int(x) - width / 2
			verticaly_object_position = int(y) - height / 2

			if direction < -width / 4:
				text += " Turn left"
				motors.move_motors(0, 35, "forward")
			elif direction > width / 4:
				text += " Turn right"
				motors.move_motors(35, 0, "forward")				
			else:
				text += " Forward"
				motors.move_motors(35, 35, "forward")	

			# if verticaly_object_position < -height / 6:
			# 	if servoDutyCycle < 5:
			# 		servoDutyCycle = 5
			# 	else:
			# 		servoDutyCycle -= 0.1

			# 	servo.changeDutyCycle(servoDutyCycle);

			# 	text += " Look up"
			# elif verticaly_object_position > height / 6:
			# 	if servoDutyCycle > 10:
			# 		servoDutyCycle = 10
			# 	else:
			# 		servoDutyCycle += 0.1
					
			# 	servo.changeDutyCycle(servoDutyCycle);

			# 	text += " Look down"
			# else: 
			# 	text += " Look forward"	

			cv2.putText(frame, text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1) #Draw the text
	else:
		motors.move_motors(0, 0, "forward")

	# show the frame
	cv2.imshow("Frame", frame)    
	cv2.imshow("Mask", mask)
	
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
 
# do a bit of cleanup
motors.cleanup_pins()
cv2.destroyAllWindows()
vs.stop()
