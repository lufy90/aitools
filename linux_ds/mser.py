
import cv2
import sys

image = cv2.imread(sys.argv[1])
mser = cv2.MSER_create()

regions, _ = mser.detectRegions(image)

# Draw MSER regions on the image
for region in regions:
    cv2.polylines(image, [region], 1, (0, 255, 0))

cv2.imshow('MSER Features', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
