import logging
import math
import os

from alive_progress import alive_bar
from numpy import asarray, mean
from PIL import Image

import Utils

logger = logging.getLogger(__name__)
InputImagePath = os.getenv("FRAMES_STORE_PATH", "Frames")
OutputImagePath = os.getenv("COLLAGES_STORE_PATH", "Collages")


def CreateAverageImage(frame_number):

    images = Utils.getAllImagesFromDirectory(
        os.path.join(InputImagePath, str(frame_number))
    )

    if not images:
        logger.error("No images provided for averaging.")
        return None

    # Ensure all images are the same size
    first_image = images[0]
    width, height = first_image.size
    for img in images:
        if img.size != (width, height):
            logger.error("All images must be the same size for averaging.")
            return None

    # Create a new image to hold the average
    average_image = Image.new("RGB", (width, height))

    allData = []

    # Sum up all pixel values
    logger.info("getting pixel data from images")
    for img in images:
        # img = Image.open(image)
        img = img.convert("RGB")  # Ensure image is in RGB mode
        allData.append(img.get_flattened_data())

    logger.info("averaging pixels")
    with alive_bar(width * height) as bar:
        for j in range(height):
            for i in range(width):

                r, g, b = 0, 0, 0
                totalImages = len(allData)

                for dataset in allData:
                    pixel = dataset[j * width + i]
                    r += pixel[0] * pixel[0]
                    g += pixel[1] * pixel[1]
                    b += pixel[2] * pixel[2]

                r = math.isqrt(r // totalImages)
                g = math.isqrt(g // totalImages)
                b = math.isqrt(b // totalImages)

                average_image.putpixel((i, j), (r, g, b))
                bar()

    average_image_path = os.path.join(
        OutputImagePath, f"frame_{frame_number}_average.jpg"
    )
    os.makedirs(OutputImagePath, exist_ok=True)
    average_image.save(average_image_path)
    logger.info(f"Saved average image to: {average_image_path}")
