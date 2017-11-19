from typing import Iterable

from PIL import Image

from core.models import BeadColor, Color
from util.color import color_distance


def downsample(image: Image.Image, width: int, height: int, keep_aspect: bool=True,
               sample_filter: int=Image.HAMMING) -> Image.Image:
    """
    Downsample an image to a lower resolution
    :param image: Source image
    :param width: Desired width
    :param height: Desired height
    :param keep_aspect: True if the aspect ratio should be maintained
    :param sample_filter: Filter to use for downsampling
    :return: A downsampled image
    """
    if keep_aspect:
        width, height = preserve_aspect_ratio(image.width, image.height, width, height)
    return image.resize((width, height), sample_filter)


def upsample(image: Image.Image, width: int, height: int, keep_aspect: bool=True,
             sample_filter: int=Image.NEAREST) -> Image.Image:
    """
    Upsample an image to a higher resolution
    :param image: Source image
    :param width: Desired width
    :param height: Desired height
    :param keep_aspect: True if the aspect ratio should be maintained
    :param sample_filter: Filter to use for upsampling
    :return: An upsampled image
    """
    if keep_aspect:
        width, height = preserve_aspect_ratio(image.width, image.height, width, height)
    return image.resize((width, height), sample_filter)


def remap(image: Image.Image, allowable_colors: Iterable[BeadColor]) -> Image.Image:
    """
    Remap the colors of the source image to the nearest allowable color
    :param image: Source image
    :param allowable_colors: Iterable of BeadColor objects indicating which colors are allowable
    :return: New image with remapped colors
    """
    new_image = image.copy()

    tmp_color = Color()
    for y in range(image.height):
        for x in range(image.width):
            px = image.getpixel((x, y))
            tmp_color.red = px[0]
            tmp_color.green = px[1]
            tmp_color.blue = px[2]

            distances = sorted([
                (color_distance(tmp_color, bead_color), bead_color) for bead_color in allowable_colors],
                key=lambda tup: tup[0])
            closest_bead = distances[0][1]
            closest_color = (closest_bead.red, closest_bead.green, closest_bead.blue)

            new_image.putpixel((x, y), closest_color)

    return new_image


def preserve_aspect_ratio(old_width: int, old_height: int, new_width: int, new_height: int) -> (int, int):
    """
    Helper function to calculate the proper width and height to maintain a given aspect ratio
    :param old_width: Source width
    :param old_height: Source height
    :param new_width: Desired width
    :param new_height: Desired height
    :return: (width, height), where width or height may be smaller than desired to maintain the source aspect ratio
    """
    aspect_ratio = old_width / old_height
    expected_width = round(new_height * aspect_ratio)
    expected_height = round(new_width / aspect_ratio)

    if new_width > expected_width:
        new_width = expected_width
    elif new_height > expected_height:
        new_height = expected_height

    return new_width, new_height
