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
import cvvideo
from coord import Point
from motion import Motion
import cProfile
import argparse
def run():
    ap = argparse.ArgumentParser(description="Stabilizes a sequence of pictures to mask shaking, jitter and other changes", version=STABILIZE_VERSION)
    ap.add_argument("input", help="Shell glob for input files (most images, eg. jpg png.. accepted)")
    ap.add_argument("output", help="Template for image output, with %%04d (or %%03d or such) to be replaced with an incrementing number")
    ag = ap.add_argument_group("Multiple Image Input/Output")
    ag.add_argument("--multifile-in-start", type=int, metavar='N', help="Start the input images at the Nth image (counting from 0)")
    ag.add_argument("--multifile-in-stop", type=int, metavar='N', help="Stop the input images at the Nth image (counting from 0)")
    ag.add_argument("--multifile-out-start", type=int, metavar='N', help="Start counting output images at N")
    args = ap.parse_args()
                
    il = cvvideo.Input(filename=args.input)
    ol = cvvideo.Output(filename=args.output, res=il.res + Point(256,256))
    m = Motion(il.res)
    lastmv = Point(0,0)
    
    for image0, image1 in il.pairs():
        lastmv = m.minisearch(image0, image1, pointgen=m.diamond_pointgen, lastmv=lastmv)
        image1.motion = image0.motion + lastmv
        print image1.motion
        image1.motion.truncate(Point(128, 128))
        newimage = m.compensate(image1)
        ol.push(newimage)

cProfile.run("run()", "/tmp/stabprof")
import pstats
s = pstats.Stats("/tmp/stabprof")
s.strip_dirs().sort_stats("cumulative").print_stats(25)
