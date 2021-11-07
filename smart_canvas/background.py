from threading import Thread
import time

import cv2


class ForegroundMask:
    """
    Class that gets the foreground mask with a dedicated thread.
    """

    def __init__(self, src=0):
        self.back_sub = cv2.createBackgroundSubtractorMOG2(
            history=20, varThreshold=16, detectShadows=False)
        self.fg_mask = None
        self.frame = None
        self.stopped = False

    def apply(self):
        while not self.stopped:
            time.sleep(0.25)
            if self.frame is None:
                continue
            self.fg_mask = self.back_sub.apply(self.frame)

    def start(self):
        Thread(target=self.apply, args=()).start()
        return self

    def stop(self):
        self.stopped = True
