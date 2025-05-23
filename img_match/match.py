
import cv2
import numpy as np
import matplotlib.pyplot as plt

def match_feature(icon_path, img_path):
    icon = cv2.imread(icon_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(icon,None)
    kp2, des2 = sift.detectAndCompute(img, None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    #matchesMask = [[0,0] for i in range(len(matches))]
    #for i,(m,n) in enumerate(matches):
    #    if m.distance < 0.7*n.distance:
    #        print(m,n)
    #        matchesMask[i]=[1,0]
    #draw_params = dict(matchColor = (0,255,0),
    #               singlePointColor = (255,0,0),
    #               matchesMask = matchesMask,
    #               flags = cv2.DrawMatchesFlags_DEFAULT)

    #img3 = cv2.drawMatchesKnn(icon,kp1,img,kp2,matches,None,**draw_params)

    #plt.imshow(img3,),plt.show()
    #matches = sorted(matches, key=lambda x: x.distance)
    img_matches = cv2.drawMatches(icon, kp1, img, kp2, matches[:1], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imshow('Matches', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




def match(icon_path, img_path, threshold=0.6):
    # match icon position in img
    img = cv2.imread(img_path)
    icon = cv2.imread(icon_path)

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    icon_hsv = cv2.cvtColor(icon, cv2.COLOR_BGR2HSV)
    
    result = cv2.matchTemplate(img_hsv, icon_hsv, cv2.TM_CCOEFF_NORMED)
    
    threshold = threshold
    loc = np.where(result >= threshold)
    
    number = 1
    for pt in zip(*loc[::-1]):
        location = ((pt[0] + icon.shape[1], pt[1] + icon.shape[0]))
        print(f'No. {number}: find icon at {location}')
        cv2.rectangle(img, pt, (pt[0] + icon.shape[1], pt[1] + icon.shape[0]), (0, 255, 0), 2)
        number = number + 1

    #img.resize((540, 970))
    #
    #cv2.imshow("Detected Icon", img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

def detect_icons(img_path):

    # Load the input image
    img = cv2.imread(img_path)
    
    # Convert the image to the HSV color space
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define the color range for the icon (e.g., detecting a red icon)
    # These values depend on the color of your icon, use a tool to pick the correct values
    lower_color = np.array([0, 50, 50])  # Lower bound for red color in HSV
    upper_color = np.array([10, 255, 255])  # Upper bound for red color in HSV
    
    # Create a mask for the selected color
    mask = cv2.inRange(hsv_img, lower_color, upper_color)
    
    # Optionally, apply some morphological operations (erosion, dilation) to clean up the mask
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))  # Closing
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw bounding boxes around the detected icons
    for contour in contours:
        # Filter out small contours based on area (optional)
        if cv2.contourArea(contour) > 500:  # Adjust area threshold as necessary
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Show the result
    cv2.imshow("Detected Icons", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    import sys
    #match(sys.argv[1], sys.argv[2])
    #detect_icons(sys.argv[1])
    match_feature(sys.argv[1],sys.argv[2])
