from threading import Thread
import time

import cv2


class VideoRead:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, q_producer, src=0):
        self.video_queue = q_producer
        self.stream = cv2.VideoCapture(src)
        (self.status, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped and self.status:
            (self.status, self.frame) = self.stream.read()
            self.video_queue.put(self.frame)

    def stop(self):
        self.stopped = True
        self.video_queue.put(None)
        self.stream.release()
