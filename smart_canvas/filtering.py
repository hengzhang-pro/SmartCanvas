""" filtering.py """

# Default packages
import itertools

# External packages
import cv2
import numpy as np

# Internal packages

def filter_oil_painting(frame):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6,6))
    morph = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    result = cv2.normalize(morph, None, 20, 255, cv2.NORM_MINMAX)
    return result

def mosaic_filter(frame):
    width = frame.shape[1]
    height = frame.shape[0]
    rect = (0,0, width, height)
    subdiv = cv2.Subdiv2D(rect)
    for n in range(1000):
        subdiv.insert([np.random.randint(0,width-1), np.random.randint(0,height-1)])

    (facets, centers) = subdiv.getVoronoiFacetList([])
    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)
        ifacet = np.array(ifacet_arr, np.int)
        mask = np.full((height, width), 0, dtype=np.uint8)
        cv2.fillConvexPoly(mask, ifacet, (255,255,255))
        ifacets = np.array([ifacet])

        res = cv2.bitwise_or(frame, frame, mask=mask)
        col_mean = cv2.mean(res, mask)

        cv2.fillConvexPoly(frame, ifacet, col_mean)
        #cv2.polylines(img, ifacets, True, (0,0,0), 1)
    return frame

def canvas_filter(frame):
    tile = cv2.imread("struc.pgm")
    width = frame.shape[1]
    height = frame.shape[0]
    x_count = int(width / tile.shape[0]) + 1
    y_count = int(height / tile.shape[1]) + 1

    tiled = np.tile(tile, (y_count, x_count, 1))
    canvas_bg = tiled[0:frame.shape[0], 0:frame.shape[1]]
    kernel = np.array([[0.5,0],[0,0.5]])

    canvas_bg = cv2.filter2D(canvas_bg, -1, kernel=kernel)
    alpha = 0.85
    frame = cv2.addWeighted(frame, alpha, canvas_bg, 1 - alpha, 0)
    return frame

def tv_60(frame):
    #cv2.namedWindow('image')
    #cv2.createTrackbar('val', 'image', 0, 255, nothing)
    #cv2.createTrackbar('threshold', 'image', 0, 100, nothing)
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #thresh = cv2.getTrackbarPos('threshold', 'image')
    thresh = 50
    val = 125
    for i in range(height):
        for j in range(width):
            if np.random.randint(100) <= thresh:
                if np.random.randint(2) == 0:
                    gray[i,j] = min(gray[i,j] + np.random.randint(0, val+1), 255)
    # adding noise to image and setting values > 255 to 255.
                else: gray[i, j] = max(gray[i, j] - np.random.randint(0, val+1), 0)
    # subtracting noise to image and setting values < 0 to 0.
    return gray

catalog = {
    'oil_painting': lambda x: filter_oil_painting(x),
    'watercolor': lambda x: cv2.stylization(x, sigma_s=60, sigma_r=0.6),
    'gray': lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY),
    'bw_sketch': lambda x: cv2.pencilSketch(x, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[0],
    'color_sketch': lambda x: cv2.pencilSketch(x, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[1],
    'blur': lambda x: cv2.GaussianBlur(x, (21, 21), 0),
    'mosaic': lambda x: mosaic_filter(x),
    'canvas': lambda x: canvas_filter(x),
    'tv_60': lambda x: tv_60(x)
}

carousel = itertools.cycle(catalog)
