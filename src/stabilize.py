#!/usr/bin/python
'''
Created on Jun 5, 2012
 but made from a file created 4 days earlier

@author: Sean Gallagher
@summary: Stabilize a set of images and make their differences less noticeable
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''
STABILIZE_VERSION = "0.1a"
try:
    # Numpypy must be imported before numpy to enable pypy's beta numpy
    import numpypy
except ImportError:
    pass

import multifile
from coord import Point
from motion import Motion

import argparse
ap = argparse.ArgumentParser(description="Stabilizes a sequence of pictures to mask shaking, jitter and other changes", version=STABILIZE_VERSION)
ap.add_argument("input", help="Shell glob for input files (most images, eg. jpg png.. accepted)")
ap.add_argument("output", help="Template for image output, with %%04d (or %%03d or such) to be replaced with an incrementing number")
args = ap.parse_args()
            
il = multifile.Input(args.input)
ol = multifile.Output(args.output, il.res + Point(128,128))
m = Motion(il.res)
last_relative_motion = Point(0,0)

for image0, image1 in il.filePairs():
    last_relative_motion = m.search(image0, image1, pointgen=m.diamond_pointgen, start=last_relative_motion)
    image1.motion = image0.motion + last_relative_motion
    print image1.motion
    image1.motion.truncate(256)
    newimage = m.compensate(image1)
    ol.push(newimage)
