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
import option

import cProfile
import argparse
def run():
    ap = argparse.ArgumentParser(description="Stabilizes video to mask shaking, jitter and other changes", version=STABILIZE_VERSION)
    ap.add_argument("input", help="Shell glob for input files (most images, eg. jpg png.. accepted)")
    ap.add_argument("output", help="Template for image output, with %%04d (or %%03d or such) to be replaced with an incrementing number")
    ap.add_argument("--in-type", type=str, default="guess", choices=["video", "images", "guess"], help="Choose between image and video-file inputs [default: guess]")
    ap.add_argument("--out-type", type=str, default="guess", choices=["video", "images", "guess"], help="Choose between image and video-file outputs [default: guess]")
    
    for optiongroup in option.all_groups:
        argumentgroup = ap.add_argument_group(optiongroup.description)
        for opt in optiongroup:
            argumentgroup.add_argument('--%s-%s' %(optiongroup.name,opt), type=optiongroup[opt]['type'], default=optiongroup[opt]['value'], help=optiongroup[opt]['help'])
    
    args = ap.parse_args()
    
    for optiongroup in option.all_groups:
        for opt in optiongroup:
            optiongroup[opt]['value'] = getattr(args, '%s_%s' %(optiongroup.name,opt.replace('-', '_')))
    
    if (args.in_type == "guess" and "%0" in args.input) or args.in_type == "images":
        # Guess this is a sequence of images - or we were told
        inputList = multifile.Input(shglob=args.input, # Positional argument of input
                        start=args.mf_in_start, # Arguments for which images to start/stop counting on
                        stop=args.mf_in_stop)
    else:
        # Guess this is a video
        inputList = cvvideo.Input(filename=args.input)
        
    if (args.out_type == "guess" and "%0" in args.output) or args.out_type == "images":
        # Guess this is a sequence of images - or we were told
        outputList = multifile.Output(shglob=args.output,
                         start=args.mf_out_start)
    else:
        outputList = cvvideo.Output(filename=args.output,
                                    res=inputList.res + Point(256,256))
    m = Motion(inputList.res)
    
    for image0, image1 in inputList.pairs():
        image1.motion = m.minisearch(image0, image1)
        print image1.motion
        #image1.motion.truncate(Point(128, 128))
        newimage = m.compensate(image1)
        outputList.push(newimage)

cProfile.run("run()", "/tmp/stabprof")
import pstats
s = pstats.Stats("/tmp/stabprof")
s.strip_dirs().sort_stats("cumulative").print_stats(25)
