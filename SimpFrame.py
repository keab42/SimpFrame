import argparse
import logging
import os
import random
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

import FrameGetter
import ImageAverager
import ImageStitcher
import Utils

load_dotenv()

logger = logging.getLogger(__name__)
maxFrames = int(os.getenv("LONGEST_VIDEO_IN_SECONDS", 1320)) * int(
    os.getenv("FRAME_RATE", 24)
)

parser = argparse.ArgumentParser(
    description="Extract a single frame from all videos in a folder, stitch them into a collage, and optionally create an average image."
)
parser.add_argument(
    "--loglevel",
    type=str,
    default="INFO",
    help="Set the logging level. Default is INFO.",
)
parser.add_argument(
    "--generate-average-image",
    action="store_true",
    help="If set, also generate an average image for the selected frame number.",
)
args = parser.parse_args()


def main():
    setup_logger()
    frameNum = random.randint(0, maxFrames)
    logging.info(f"Selected random frame number: {frameNum}")
    FrameGetter.getFrameFromAllVideosInFolder(frameNum, os.getenv("VIDEO_FOLDER_PATH"))
    ImageStitcher.stitchFrames(frameNum)
    if args.generate_average_image:
        ImageAverager.CreateAverageImage(frameNum)
    Utils.cleanupFrames(frameNum)


def setup_logger():
    if not os.path.exists("Logs"):
        try:
            os.makedirs("Logs")
        except Exception as e:
            logging.error("Could not create Logs directory: " + str(e))

    logfile = os.path.join("Logs", "SimpFrame.log")
    logging.basicConfig(
        handlers=[
            RotatingFileHandler(logfile, maxBytes=1000000, backupCount=7),
            logging.StreamHandler(),
        ],
        level=args.loglevel.upper(),
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


if __name__ == "__main__":
    main()
