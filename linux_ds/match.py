
import numpy as np
import cv2
import sys


def match_feature(image1, image2, strip=0.2, ratio=0.7, debug=True, **kwargs):
    w1,h1,_ = image1.shape
    w2,h2,_ = image2.shape

    params = dict(
            enable_precise_upscale=True,
            contrastThreshold=0.1,
            edgeThreshold=20,
            sigma=3,
            nOctaveLayers=5
            )
    sift1 = cv2.SIFT_create(nfeatures=int(w1*h1/200), **params)
    sift2 = cv2.SIFT_create(nfeatures=int(w2*h2/500), **params)
    keypoint1, descriptors1 = sift1.detectAndCompute(image1, None)
    keypoint2, descriptors2 = sift2.detectAndCompute(image2, None)
    index_params = dict(algorithm=0, trees=20)
    search_params = dict(checks=150)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    good_matches = [[0, 0] for i in range(len(matches))]
    good_poses = []
    for i, (m, n) in enumerate(matches):
        if m.distance < ratio*n.distance:
            good_matches[i] = [1, 0]
            good_poses.append(keypoint2[m.trainIdx].pt)
    if debug:
        show(image2, good_poses, (5,5))
    return good_poses


def multi_scale_template_matching(image, template, scales, method=cv2.TM_CCOEFF_NORMED, threshold=0.8):
    best_match = None
    best_scale = None
    max_val = threshold
    for scale in scales:
        resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
        if resized_template.shape[0] > image.shape[0] or resized_template.shape[1] > image.shape[1]:
          continue
        res = cv2.matchTemplate(image, resized_template, method)
        min_val, cur_max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if cur_max_val > max_val:
            max_val = cur_max_val
            best_match = max_loc, resized_template.shape
            best_scale = scale
    return best_match, best_scale, max_val

def test2_match():
    img = cv2.imread(sys.argv[2])
    temp = cv2.imread(sys.argv[1])
    res = multi_scale_template_matching(img, temp, np.arange(0.5, 2, 0.1))
    h,w,_ = res[0][1]
    show(img, [res[0][0]], (w,h))
    print(res)

def test1_match():
    image1 = cv2.imread(sys.argv[1])
    image2 = cv2.imread(sys.argv[2])
    return match_feature(image1,image2)

def test_match():
    # load the images
    image1 = cv2.imread(sys.argv[1])
    image2 = cv2.imread(sys.argv[2])
    w,h,_ = image1.shape
    strip = 0.2
    w1=int(w*(1-strip))
    h1=int(h*(1-strip))
    x=int(w*strip/2)
    y=int(h*strip/2)
    

    image1 = image1[y:y+h1,x:x+w1]
    
    #img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    #img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Initiate SIFT detector
    args = dict(
            enable_precise_upscale=True,
            contrastThreshold=0.1,
            edgeThreshold=10,
            sigma=2,
            nOctaveLayers=3
            )
    sift1 = cv2.SIFT_create(nfeatures=20, **args)
    sift2 = cv2.SIFT_create(nfeatures=1000, **args)
    #sift = cv2.SIFT_create()
    
    # find the keypoints and descriptors with SIFT
    keypoint1, descriptors1 = sift1.detectAndCompute(image1, None)
    keypoint2, descriptors2 = sift2.detectAndCompute(image2, None)
    
    # finding nearest match with KNN algorithm
    index_params = dict(algorithm=0, trees=10)
    search_params = dict(checks=10)   # or pass empty dictionary
    
    # Initialize the FlannBasedMatcher
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    Matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    
    # Need to draw only good matches, so create a mask
    good_matches = [[0, 0] for i in range(len(Matches))]
    good_match_pos = []
    
    # Ratio Test
    for i, (m, n) in enumerate(Matches):
        print('match:', m,n)
        if m.distance < 0.9*n.distance:
            good_matches[i] = [1, 0]
            good_match_pos.append(keypoint2[m.trainIdx].pt)

    print('good_match_pos:', good_match_pos)
    
    # Draw the matches using drawMatchesKnn()
    Matched = cv2.drawMatchesKnn(image1,
                                 keypoint1,
                                 image2,
                                 keypoint2,
                                 Matches,
                                 outImg=None,
                                 matchColor=(0, 155, 0),
                                 singlePointColor=(0, 255, 255),
                                 matchesMask=good_matches,
                                 flags=0
                                 )
    
    # Displaying the image
    #cv2.imwrite('Match.jpg', Matched)
    #print('Matched:', Matched)
    resized_matched = cv2.resize(Matched, (960,540))
    cv2.namedWindow("Normal Window", cv2.WINDOW_NORMAL)
    cv2.imshow('Matched', resized_matched)
    cv2.resizeWindow("Normal Window", 600, 400)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def show(img, pts, size, color=(0,255,0)):
    for pt in pts:
        pt = [int(i) for i in pt]
        cv2.rectangle(img, pt, (pt[0] + size[0], pt[1] + size[1]), color, 2)
    resized = cv2.resize(img, (960,540))
    cv2.namedWindow("result", cv2.WINDOW_NORMAL)
    cv2.imshow("result", img)
    cv2.resizeWindow("result", 960,540)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print(test2_match())
