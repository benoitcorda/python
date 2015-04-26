#!/usr/bin/env python

import ffmpeg

import datetime
import logging
import math
from optparse import OptionParser
import os.path
import string
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MovieCutterError(Exception):
  pass

def parseInputFileCuts(filename):
  cuts = []
  f = open(filename, "r")
  for line in f:
    start, end = line.strip().split(" ")
    sHours, sMinutes, sSecs = start.split(":")
    eHours, eMinutes, eSecs = end.split(":")
    duration = '%02d:%02d:%02d' % (int(eHours) - int(sHours),
                                   int(eMinutes) - int(sMinutes),
                                   int(eSecs) - int(sSecs))
    cuts.append([start, duration])
  return cuts

def cutVideo(cuts, input, output):
  inFile = os.path.abspath(input)
  outputVideo, extension = os.path.splitext(os.path.abspath(output))
  zfill = int(math.log(len(cuts), 10) + 1)

  for i in xrange(len(cuts)):
    outFile = outputVideo +"_"+ string.zfill(i,zfill) + extension
    start, duration = cuts[i]
    params = [
      "-vcodec", "copy",
      "-acodec", "libfaac",
      "-ss", start,
      "-t", duration,
    ]
    conv = ffmpeg.FFMpeg().convert(inFile, outFile, params)
    for timecode in conv:
      time = datetime.timedelta(seconds=timecode)
      sys.stdout.write('\r')
      sys.stdout.write("Wrote {0} of {1}".format(time, duration))
      sys.stdout.flush()
    sys.stdout.write("\nDone.")
    sys.stdout.flush()

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-f", "--file", dest="filename",
                    help="""file containing the cuts one line should be:
                    startTime stopTime
                    Time format is HOURS:MM:SS.MICROSECONDS""",
                    metavar="FILE")
  parser.add_option("-i", "--input", dest="videoIn",
                      help="video input file", metavar="VIDEO")
  parser.add_option("-o", "--output", dest="videoOut",
                      help="video output file", metavar="VIDEO")
  (options, args) = parser.parse_args()

  if not options.filename or not os.path.exists(options.filename):
    raise MovieCutterError("Cuts Input file doesn't exist")
  if not options.videoIn or not os.path.exists(options.videoIn):
    raise MovieCutterError("Input video doesn't exist")
  if not options.videoOut:
    logger.warning("output file not provided default to 'out_XX.mp4'")
    options.videoOut = "out.mp4"

  cuts = parseInputFileCuts(options.filename)
  cutVideo(cuts, options.videoIn, options.videoOut)