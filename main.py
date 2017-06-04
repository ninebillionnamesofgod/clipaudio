#!/usr/bin/env python
#-*- coding: utf-8 -*-

import soundfile as sf
import sounddevice as sd
import curses
from curses import wrapper
import glob
import sys
import numpy as np
import matplotlib.pyplot as plt
import logging
from silence import split_on_silence

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
FILE_TYPE = '*.flac'
MIN_UTTERANCE_DURATION=0.7
MAX_UTTERANCE_DURATION=2.0
UTTERANCE_STEP=0.1
SNR = 1e2
STEP_SIZE = 0.1
SMALL_STEP=0.1
BIG_STEP=0.2
SILENCE_THRESHOLD=-26
MIN_SILENCE=1000

logger = logging.getLogger(__file__)
filelog = logging.FileHandler(__file__ + ".log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
filelog.setFormatter(formatter)
logger.addHandler(filelog)
logger.setLevel(logging.DEBUG)

def clip_file(stdscr, filename, width, height):
    stdscr.clear()
    logger.info("filename: {}".format(filename))
    file_id = filename.split("/")[1].split(".")[0]
    stdscr.addstr(0, int(width/2)-10, "Current file: {}".format(filename))
    data, rate = sf.read(filename)
    small_step = int(rate*SMALL_STEP)
    big_step = int(rate*BIG_STEP)
    clips = [x for x in split_on_silence(data, rate, min_silence=MIN_SILENCE, silence_thresh=SILENCE_THRESHOLD) if len(x) > 0]
    i = 1
    if len(clips) == 0:
        logger.info("no clips found")
        return
    stdscr.addstr(1, int(width/2), "Number of clips: {}".format(len(clips)))
    for clip in clips:
        stdscr.move(2, 0)
        stdscr.clrtoeol()
        stdscr.addstr(2, int(width/2), "Clip: {}".format(i))
        start = 0
        end = len(clip)
        while True:
            stdscr.move(4,0)
            stdscr.clrtoeol()
            stdscr.move(5,0)
            stdscr.clrtoeol()
            stdscr.addstr(5, 3, "Start: {},{:.5f}s".format(start, start/rate))
            stdscr.addstr(5, width-20, "End: {},{:.5f}s".format(end, end/rate))
            stdscr.addstr(4, int(width/2), "Duration: {:.5f}s".format((end - start)/rate))
            stdscr.refresh()
            short_clip = clip[start:end]
            sd.play(short_clip, rate, blocking=True)
            k = stdscr.getkey()
            if k.upper() == 'A':
                start -= big_step
                if start < 0:
                    start = 0
            elif k.upper() == 'S':
                start -= small_step
                if start < 0:
                    start = 0
            elif k.upper() == 'D':
                start += small_step
                if start >= end:
                    start = end - small_step
            elif k.upper() == 'F':
                start += big_step
                if start >= end:
                    start = end - big_step
            elif k.upper() == 'H':
                end -= big_step
                if end <= start:
                    end = start + big_step
            elif k.upper() == 'J':
                end -= small_step
                if end <= start:
                    end = start - small_step
            elif k.upper() == 'K':
                end += small_step
                if end > len(clip):
                    end = len(clip)
            elif k.upper() == 'L':
                end += big_step
                if end > len(clip):
                    end = len(clip)
            elif k.upper() == 'Y':
                #mark Yes
                logger.info("saving god clip: god-{}-{:02d}.flac".format(file_id, i))
                sf.write("{}/god-{}-{:02d}.flac".format(OUTPUT_DIR, file_id, i), short_clip, rate)
                i += 1
                break
            elif k.upper() == 'N':
                #mark No
                logger.info("saving no god clip: no-god-{}-{:02d}.flac".format(file_id, i))
                sf.write("{}/no-god-{}-{:02d}.flac".format(OUTPUT_DIR, file_id, i), short_clip, rate)
                i += 1
                break
            elif k.upper() == 'X':
                #go to next clip
                i += 1
                break
            elif k.upper() == 'Q':
                sys.exit(1)
            elif k.upper() == 'Z':
                # Z - Exit current file
                logger.info("skipping current file: processed {} out of {} clips".format(i, len(clips)))
                return
            else:
                continue

def main_dir(stdscr):
    height, width= stdscr.getmaxyx()
    for filename in glob.glob("{}/{}".format(INPUT_DIR, FILE_TYPE)):
        clip_file(stdscr, filename, width, height)

def main_file(stdscr):
    height, width = stdscr.getmaxyx()
    clip_file(stdscr, sys.argv[1], width, height)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        wrapper(main_file)
    else:
        wrapper(main_dir)
