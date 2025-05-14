
import cv2
import sys
image = cv2.imread(sys.argv[1])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

brisk = cv2.BRISK_create()
kp, des = brisk.detectAndCompute(gray, None)

image = cv2.drawKeypoints(image, kp, None)
cv2.imshow('BRISK Features', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
