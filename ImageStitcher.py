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


def createCollage(images, frame_number):
    outputPath = os.getenv("COLLAGES_STORE_PATH", "Collages")
    totalImages = len(images)

    col_width, row_height = images[0].size
    logging.info(f"thumbnail size = {col_width} x {row_height}")

    logging.info(f"Number of images: {totalImages}")
    grid_size = getGridSize(len(images))
    totalRows = grid_size[0]
    totalColumns = grid_size[1]
    logging.info(f"Grid size: {totalRows} rows x {totalColumns} columns")
    remainder = totalImages % totalColumns

    os.makedirs(outputPath, exist_ok=True)

    # Create a new blank image with the appropriate size
    grid_image = Image.new("RGB", (totalColumns * col_width, totalRows * row_height))
    logging.info(f"Full res image size = {grid_image.size}")

    # Paste each image into the grid
    with alive_bar(totalImages) as bar:
        for index, img in enumerate(images):
            row = index // totalColumns
            col = index % totalColumns

            # scale large images down to fit in the grid cell
            if img.size > (col_width, row_height):
                img = Utils.getResizedImage(img, (col_width, row_height))

            # Centre the final image in the grid if the number of images is not a perfect square
            if row == totalRows - 1 and remainder > 0:
                # Calculate the starting x position to center the last row
                start_x = (totalColumns - (totalImages % totalColumns)) * img.width // 2
                grid_image.paste(img, (start_x + col * img.width, row * img.height))
            else:
                grid_image.paste(img, (col * col_width, row * row_height))

            bar()

    fullResPath = os.path.join(outputPath, f"frame_{frame_number}_fullRes.jpg")
    logging.info(f"Saving full-resolution image to: {fullResPath}")
    grid_image.save(fullResPath)

    postable_image = Utils.getImageThumbnail(grid_image, (1920, 1080))
    postableResPath = os.path.join(outputPath, f"frame_{frame_number}.jpg")
    logging.info(f"Saving final image to: {postableResPath}")
    postable_image.save(postableResPath)


def createMosaic(images, frame_number):
    outputPath = os.getenv("MOSAICS_STORE_PATH", "Mosaics")
    grid_size = getGridSize(len(images))
    totalRows = grid_size[0]
    totalColumns = grid_size[1]
    total_width, total_height = images[0].size
    totalImages = len(images)

    os.makedirs(outputPath, exist_ok=True)

    mosaic_image = Image.new("RGB", (total_width, total_height))

    logging.info(
        f"Final Image = {total_width} x {total_height}. {totalColumns} Columns by {totalRows} Rows."
    )

    tile_width = total_width // totalColumns
    tile_height = total_height // totalRows
    logging.info(f"Tile size = {tile_width} x {tile_height}")

    with alive_bar(totalImages) as bar:
        for index, img in enumerate(images):
            row = index // totalColumns
            col = index % totalColumns

            # scale images so that we can get the correction section
            if img.size[0] != total_width or img.size[1] != total_height:
                img = Utils.getResizedImage(img, (total_width, total_height))

            left = tile_width * col
            upper = tile_height * row

            tile = img.crop((left, upper, left + tile_width, upper + tile_height))
            mosaic_image.paste(tile, (left, upper))

            bar()

    save_path = os.path.join(outputPath, f"mosaic{frame_number}.jpg")
    logging.info(f"Saving mosaic image to: {save_path}")
    mosaic_image.save(save_path)


def stitchFrames(frame_number):
    frameDir = Utils.getFramesDirectory(frame_number)
    if not frameDir:
        return

    images = Utils.getAllImagesFromDirectory(frameDir)

    if images:
        createCollage(images, frame_number)
        createMosaic(images, frame_number)
    else:
        print("No valid images to create collage.")
