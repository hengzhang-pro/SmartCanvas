from threading import Thread
import cv2


class VideoRead:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.status, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.status:
                self.stop()
            else:
                (self.status, self.frame) = self.stream.read()
        self.stream.release()

    def stop(self):
        self.stopped = True