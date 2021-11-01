import cv2
import itertools

def filter_oil_painting(frame):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6,6))
    morph = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    result = cv2.normalize(morph, None, 20, 255, cv2.NORM_MINMAX)
    return result

filters = {
    'oil_painting': lambda x: filter_oil_painting(x),
    'gray': lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY),
    'watercolor': lambda x: cv2.stylization(x, sigma_s=60, sigma_r=0.6),
    'bw_sketch': lambda x: cv2.pencilSketch(x, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[0],
    'color_sketch': lambda x: cv2.pencilSketch(x, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[1],
    'blur': lambda x: cv2.GaussianBlur(x, (21, 21), 0),
}

def main():
    filter_carousel = itertools.cycle(filters)
    current_filter = filters[next(filter_carousel)]
    device = cv2.VideoCapture(0)

    while(True):
        _, frame = device.read()
        filtered = current_filter(frame)
        cv2.imshow('output', filtered)

        key = cv2.waitKey(1)
        if key == ord('q'): 
            break
        if key == ord('n'): 
            current_filter = filters[next(filter_carousel)]
        
    cv2.destroyWindow('output')
    device.release()
    exit(0)
   
if __name__ == '__main__':
    main()
