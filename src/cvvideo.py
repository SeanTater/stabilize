'''
Created on Jun 5, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''
# Used to import images into arrays
import cv2

from frame import Frame
from coord import Point
from option import OptGroup
opts = OptGroup('v', "Video Input/Output")
opts["out-fourcc"] = dict(type=str, metavar="CODE", value="XVID", help="Four character code for the video format (e.g. XVID, DIVX, FMP4")
opts["out-fps"] = dict(type=float, metavar="FPS", value=29.97, help="Output frames per second")

import struct
class Input(object):
    def __init__(self, filename):
        self.video = cv2.VideoCapture(filename)
        #NOTE: This means that the first file won't be closed until the end
        if not self.video.isOpened():
            raise IOError, "The video doesn't seem to have opened. Does the file exist? Is it in a supported format?"
        more, arr = self.video.read()
        if not more:
            raise IOError, "The video is empty"
        self.firstFrame = Frame(array=arr)
        # Images and matrices use opposite coordinates (in matrices, it's height, width, channel, in images it's width, height (and all three channels are one tuple)
        self.res = Point(*arr.shape)
    
    def pairs(self):
        # A generator that yields the previous and next files through the whole list
        lastFrame = self.firstFrame
        more, arr = self.video.read()
        nextFrame = Frame(array=arr)
        while True:
            yield (lastFrame, nextFrame)
            lastFrame = nextFrame
            more, arr = self.video.read()
            if not more: break
            nextFrame = Frame(array=arr)

class Output(object):
    def __init__(self, filename, res):
        fourcc = struct.unpack("i", opts("out-fourcc"))[0]
        self.video = cv2.VideoWriter(filename, fourcc, opts("out-fps"), res.r)
        self.res = res
    
    def push(self, frame):
        self.video.write(frame.rgb)