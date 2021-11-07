from threading import Thread
import time

import cv2


class VideoRead:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.status, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            time.sleep(0.01)
            if not self.status:
                self.stop()
            else:
                (self.status, self.frame) = self.stream.read()
        self.stream.release()

    def stop(self):
        self.stopped = True
