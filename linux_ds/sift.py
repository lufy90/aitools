
import cv2
import sys

image = cv2.imread(sys.argv[1])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

sift = cv2.SIFT_create(
        nfeatures=20,
        nOctaveLayers=3,
        contrastThreshold=0.04,
        edgeThreshold=100,
        sigma=3.5,
        )
kp, des = sift.detectAndCompute(gray, None)

image = cv2.drawKeypoints(image, kp, None)
cv2.imshow('SIFT Features', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
