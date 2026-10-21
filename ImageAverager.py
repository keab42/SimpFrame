import logging
import os

import numpy
from alive_progress import alive_bar
from numpy import asarray, mean
from PIL import Image

import Utils

logger = logging.getLogger(__name__)

def CreateAverageImage(frame_number):
    inputPath = os.getenv("FRAMES_STORE_PATH")
    outputPath = os.getenv("AVERAGE_IMAGE_STORE_PATH")

    if not inputPath:
        logger.error("Environment variable 'FRAMES_STORE_PATH' is not set")
        return None

    if not outputPath:
        logger.error("Environment variable 'AVERAGE_IMAGE_STORE_PATH' is not set")
        return None

    images = Utils.getAllImagesFromDirectory(os.path.join(inputPath, str(frame_number)))

    if not images:
        logger.error("No images provided for averaging.")
        return None

    totalImages = len(images)
    average_image_path = os.path.join(outputPath, f"frame_{frame_number}_average.jpg")

    # Ensure all images are the same size
    first_image = images[0]
    frame_width, frame_height = first_image.size
    logging.info(f"Image size = {first_image.size}")

    # Create a new image to hold the average
    average_image = Image.new("RGB", (frame_width, frame_height))
    outputArr = numpy.zeros(
        (frame_height, frame_width, 3), dtype=numpy.float32
    )  # Initialize an array to hold the sum of pixel values

    # Sum up all pixel values
    logger.info("getting pixel data from images")
    with alive_bar(totalImages) as bar:
        for img in images:
            if img.size[0] != frame_width or img.size[1] != frame_height:
                img = Utils.getResizedImage(img, first_image.size)
            img = img.convert("RGB")  # Ensure image is in RGB mode
            imgArray = asarray(img, dtype=numpy.float32)  # Convert image to numpy array
            outputArr += numpy.square(
                imgArray
            )  # Add the square of pixel values to the output array
            bar()

    outputArray = numpy.sqrt(
        outputArr / totalImages
    )  # Calculate the square root of the average of squared values
    intArray = numpy.array(
        outputArray, dtype=numpy.uint8
    )  # Convert to uint8 for image saving
    average_image = Image.fromarray(intArray, "RGB")
    average_image = average_image.convert("RGB")

    os.makedirs(outputPath, exist_ok=True)
    average_image.save(average_image_path)
    logger.info(f"Saved average image to: {average_image_path}")
