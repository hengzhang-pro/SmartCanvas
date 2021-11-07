import time

import moderngl
import cv2

from smart_canvas.capture import VideoRead
from smart_canvas.core import CanvasCore
from smart_canvas.window import Window


class SmartRender(Window):
    """
    Class that renders OpenGL window with processed video output
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video = VideoRead(0).start()
        self.core = CanvasCore().start()

    def render(self, _time, frame_time):
        time.sleep(0.05)
        self.core.frame = self.video.frame
        out_frame = self.core.out_frame
        if (out_frame is None):
            return
        self.frame_texture.write(cv2.flip(self.core.out_frame, 0))
        self.frame_texture.use(0)
        self.quad.render(mode=moderngl.TRIANGLE_STRIP)

    def close(self):
        self.video.stop()
        self.core.stop()


if __name__ == '__main__':
    SmartRender.run()
