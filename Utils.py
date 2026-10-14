import logging
import os
from typing import List

from PIL import Image, ImageFile

logger = logging.getLogger(__name__)


def getAllImagesFromDirectory(image_dir) -> List[ImageFile.ImageFile] | None:
    images = []

    imageFiles = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    if not imageFiles:
        logging.error(f"No image files found in directory: {image_dir}")
        return None

    for imageFile in imageFiles:
        imagePath = os.path.join(image_dir, imageFile)
        try:
            img = Image.open(imagePath)
            images.append(img)
        except Exception as e:
            logging.error(f"Error opening image {imagePath}: {e}")

    return images if images else None


def getFramesDirectory(frame_number):
    inputPath = os.getenv("FRAMES_STORE_PATH")
    if not inputPath:
        logging.error("Environment variable 'FRAMES_STORE_PATH' is not set")
        return None
    frameDir = os.path.join(inputPath, str(frame_number))
    if not os.path.exists(frameDir):
        logging.error(f"Frame directory does not exist: {frameDir}")
        return None
    return frameDir


def cleanupFrames(frame_number):
    frameDir = getFramesDirectory(frame_number)
    if frameDir and os.path.exists(frameDir):
        print(f"Cleaning up frame directory: {frameDir}")
        for imageFile in os.listdir(frameDir):
            os.remove(os.path.join(frameDir, imageFile))
        os.rmdir(frameDir)
