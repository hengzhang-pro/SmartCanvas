import os

import moderngl
from .window import Window

import numpy as np
from array import array

from threading import Thread

from .capture import VideoRead
from .core import CanvasCore

import cv2

class SmartRender(Window):
    gl_version = (3, 3)
    title = "SmartCanvas"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.program = None


        self.video = VideoRead(0).start()#self.window.source#cv2.VideoCapture("test.mp4")
        self.process = CanvasCore(self.video.frame).start()
        #self.video.stream.set(3, 1280)
        #self.video.stream.set(4, 720)
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(Window.window_size,3)]
        )

        self.program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    uv = in_uv;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D image;

                out vec4 f_color;
                in vec2 uv;

                void main() {
                    vec4 color = texture(image, uv);
                    f_color = vec4(color.b, color.g, color.r, color.a);
                }
            ''',
        )

        self.vertices = self.ctx.buffer(
            array('f',
            [
            -1,  1, 0, 1,  # upper left
            -1, -1, 0, 0, # lower left
            1,  1, 1, 1, # upper right
           1, -1, 1, 0, # lower right
        ])
        )

        self.quad = self.ctx.vertex_array(
            self.program,
            [
                (self.vertices, '2f 2f', 'in_vert', 'in_uv'),
            ]
        )
        # TODO/TOCHECK: internal parameter format. Might get better performance when using shorter format bc default includes alpha
        self.frame_texture = self.ctx.texture((640,480), 3)#, internal_format=0x8C41)

    def render(self, time, frame_time):

        self.process.frame = self.video.frame
        self.frame_texture.write(cv2.flip(self.process.frameout,0))

        self.frame_texture.use(0)
        self.quad.render(mode=moderngl.TRIANGLE_STRIP)

    def close(self):
        self.video.stop()
        self.process.stop()


if __name__ == '__main__':

    SmartRender.run()
