import logging
import os

import imageio.v3 as iio
from alive_progress import alive_bar
from dotenv import load_dotenv
from PIL import Image

logger = logging.getLogger(__name__)


def saveFrameFromVideo(video_path, frame_number):
    outputPath = os.getenv("FRAMES_STORE_PATH", "")

    logger.debug(f"Extracting frame {frame_number} from video: {video_path}")
    savePath = os.path.join(
        outputPath,
        str(frame_number),
        os.path.basename(video_path).replace(".mkv", ".png"),
    )
    os.makedirs(os.path.dirname(savePath), exist_ok=True)
    try:
        image = iio.imread(video_path, index=frame_number)
        logger.debug(f"Saving frame to: {savePath}")
        iio.imwrite(savePath, image)
    except IndexError:
        blankImage = Image.new(
            "RGB", (1920, 1080), color=(0, 0, 0)
        )  # Create a blank image
        logger.debug(f"Saving Blank frame to: {savePath}")
        blankImage.save(savePath)
        return
    except Exception as e:
        logger.error(f"Error occurred while processing video {video_path}: {e}")
        return


def getFrameFromAllVideosInFolder(frame_number, video_folder_path):

    if not os.path.exists(video_folder_path):
        logger.error(f"Video folder path does not exist: {video_folder_path}")
        return

    with alive_bar() as bar:
        for root, dirs, files in os.walk(video_folder_path):
            for file in files:
                if file.endswith(".mkv"):
                    videoPath = os.path.join(root, file)
                    saveFrameFromVideo(videoPath, frame_number)
                bar()
