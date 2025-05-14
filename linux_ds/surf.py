
import cv2
import sys

image = cv2.imread(sys.argv[1])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

surf = cv2.xfeatures2d.SURF_create(400)
kp, des = surf.detectAndCompute(gray, None)

image = cv2.drawKeypoints(image, kp, None)
cv2.imshow('SURF Features', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
