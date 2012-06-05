Stabilize
=========

INSTALL
-------
Stabilize doesn't install (yet). stabilize.py (in src/) should run without installation
To run it, you will need:
	Python Imaging Library (PIL)
	NumPy
	and a Python Interpreter
	This all should be available on debian/ubuntu/linux mint etc, with the following command:
		sudo apt-get install python-numpy python-imaging

Usage
-----
Note:
	Stabilize only takes images as input, not video yet. This means that audio is a bit tough to work in (though not impossible)
	This is expected to change in the future.

You can still use code such as this to use videos (which is what is done in development):
	# It's not good practice to make temporary directories this way but it works
	mkdir /tmp/stabilize_temp 
	# Fill in your original video file name
	avconv -i /the/original/video -f image2 /tmp/stabilize_temp/input_%04d.jpg
	stabilize.py /tmp/stabilize_temp/input_%04d.jpg /tmp/stabilize_temp/output_%04d.jpg
	# Fill in your output video file name
	avconv -f image2 -i /tmp/stabilize_temp/output_%04d.jpg /your/output/video

