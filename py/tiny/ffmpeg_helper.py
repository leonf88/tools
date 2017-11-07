#!/usr/bin/env python
# coding: utf-8

import argparse
import ffmpeg
import os
import sys
import logging
import ffmpeg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_files(rootDir, suffix):
    files = []
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if fname.lower().endswith(suffix):
                files.append(os.path.join(dirName, fname))

    return files


def run(infile, outfile):
    if not os.path.exists(infile):
        logger.error("%s not exist.", infile)

    out_basedir = os.path.dirname(outfile)
    print out_basedir
    if not os.path.exists(out_basedir):
        os.makedirs(out_basedir)

    # ffmpeg -i ${input} \
    #         -vcodec libx264 -preset medium -profile high \
    #         -crf 26
    #         -s 1280x720 \
    #         -max_muxing_queue_size 1000 \
    #         -acodec libfdk_aac -ac 2 -ar 44100 -ab 64k \
    #         -y ${output}
    stream = (
            ffmpeg.input(infile)
            .output("asdf",
                y="",
                vcodec='libx264', preset='medium', profile='high', s='1280x720', max_muxing_queue_size='1000',
                crf='26',
                acodec='libfdk_aac', ac='2', ar='44100', ab='64k')
            )

    # TODO: how to solve the unicode join problem
    logger.info("Run ffmpeg {}".format(
        # u" ".join([e.decode('utf-8') for e in stream.get_args()])
        stream.get_args()
        ))
    stream.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ffmpeg Helper.')
    parser.add_argument('-i', dest='inPath', required=True,
            help='Input Path to scan the movies files.')
    parser.add_argument('-o', dest='outPath', required=True,
            help='Output Path to store the converted files.')
    parser.add_argument('-t', dest='type', default="mp4",
            help='The type of the movies, default: mp4.')

    args = parser.parse_args()

    inp = os.path.abspath(args.inPath)
    outp = os.path.abspath(args.outPath)
    if inp == outp:
        print("Input path and output path can not be equal.")
        sys.exit(-1)
    files = list_files(inp, args.type)
    d_len = len(inp)
    for input_path in files:
        output_path = os.path.join(outp, input_path[d_len + 1:])
        filedir = os.path.dirname(output_path)
        filename = os.path.basename(output_path)
        filename.lower().replace('.'+args.type, '.mp4')
        run(input_path, output_path)
