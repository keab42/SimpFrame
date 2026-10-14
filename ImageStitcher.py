import logging
import os

from alive_progress import alive_bar
from PIL import Image

import Utils

logger = logging.getLogger(__name__)


def getGridSize(num_images):
    # Calculate the number of rows and columns for the grid
    cols = int(num_images**0.5)
    rows = (num_images + cols - 1) // cols  # Ceiling division
    return (rows, cols)


def createCollage(images, frameDir, frame_number):
    outputPath = os.getenv("COLLAGES_STORE_PATH", "Collages")
    totalImages = len(images)
    logging.info(f"Number of images: {totalImages}")
    grid_size = getGridSize(len(images))
    totalRows = grid_size[0]
    totalColumns = grid_size[1]
    logging.info(f"Grid size: {totalRows} rows x {totalColumns} columns")

    os.makedirs(outputPath, exist_ok=True)

    # Create a new blank image with the appropriate size
    grid_image = Image.new(
        "RGB", (totalColumns * images[0].width, totalRows * images[0].height)
    )
    # Paste each image into the grid

    with alive_bar(totalImages) as bar:
        for index, img in enumerate(images):
            row = index // totalColumns
            col = index % totalColumns
            # Centre the final image in the grid if the number of images is not a perfect square
            if row < totalRows - 1:
                grid_image.paste(img, (col * img.width, row * img.height))
            else:
                # Calculate the starting x position to center the last row
                start_x = (totalColumns - totalImages % totalColumns) * img.width // 2
                grid_image.paste(img, (start_x + col * img.width, row * img.height))
            bar()

    fullResPath = os.path.join(outputPath, f"frame_{frame_number}_fullRes.jpg")
    logging.info(f"Saving full-resolution image to: {fullResPath}")
    grid_image.save(fullResPath)

    postable_image = getResizedImage(grid_image, (1920, 1080))
    postableResPath = os.path.join(outputPath, f"frame_{frame_number}.jpg")
    logging.info(f"Saving final image to: {postableResPath}")
    postable_image.save(postableResPath)


def getResizedImage(image, target_size):
    # Resize the image while maintaining aspect ratio
    image.thumbnail(target_size)
    return image


def stitchFrames(frame_number):
    frameDir = Utils.getFramesDirectory(frame_number)
    if not frameDir:
        return

    images = Utils.getAllImagesFromDirectory(frameDir)

    if images:
        createCollage(images, frameDir, frame_number)
    else:
        print("No valid images to create collage.")

