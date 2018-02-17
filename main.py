#!/usr/bin/env python

from imutils.video import VideoStream
from classes.MotorsController import MotorsController
from classes.ServoController import ServoController
from classes.RelayController import RelayController
from classes.Camera import Camera
import RPi.GPIO as GPIO
import datetime
import argparse
import time
import random
import cv2
import sys
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=1, help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())
 
greenLower = (21, 100, 100)
greenUpper = (41, 255, 255)

camera = Camera(greenLower, greenUpper, args["picamera"] == 1)
time.sleep(0.5)

width = 400
height = 300

text = ''

# The time when he did last action
lastActiveTime = 0
movingTime = None
direction = None

def clean():
	motors.clean()
	relay.clean()
	servo.clean()
	camera.clean()
	GPIO.cleanup()

if __name__ == "__main__":
	motors = MotorsController()
	relay = RelayController()
	servo = ServoController()

	relay.start()

	try: 
		while True:
			frame, mask, x, y = camera.compute()

			if x != sys.maxint and y != sys.maxint:
				object_x = x - width / 2
				object_y = y - height / 2

				# Update the last active time
				lastActiveTime = time.time()

				# Activate motors
				# motors.go_to_object(object_x)

				# Activate servo
				servo.compute(object_y)
				
				cv2.putText(frame, text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
			else:
				# if time.time() - lastActiveTime > 10:
				# 	# He stayed for 10 seconds

				# 	if movingTime == None:
				# 		# How much time to move ( 2 sec )
				# 		movingTime = time.time() + 2
				# 		# Choose a random direction to move
				# 		direction = random.choice(['left', 'right'])
				# 	else:
				# 		if movingTime - time.time() > 0:
				# 			if direction == 'left':
				# 				motors.move_motors(-100, 100)
				# 			else:
				# 				motors.move_motors(100, -100)							
				# 		else:
				# 			movingTime = None
				# 			lastActiveTime = time.time()
				# else:
				# 	motors.stop()
				print 'Can not find something'
				# motors.stop()

			# show the frame
			cv2.imshow("Frame", frame)    
			cv2.imshow("Mask", mask)
			
			key = cv2.waitKey(1) & 0xFF

			if key == ord("q"):
				clean()
				break		

	except Exception as e: 
		print e
		clean()