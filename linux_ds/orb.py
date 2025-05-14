
import cv2
import sys

image = cv2.imread(sys.argv[1])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

orb = cv2.ORB_create()
kp, des = orb.detectAndCompute(gray, None)

image = cv2.drawKeypoints(image, kp, None)
cv2.imshow('ORB Features', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
