from . import Image


def visualize(image_data: bytes, width: int, height: int, color_type: int, palette: bytes) -> None:
    """Отвечает за попиксельную отрисовку изображения"""
    color_modes = {
        0: "L",   # Grayscale
        2: "RGB", # RGB
        3: "P",   # Indexed-color
        4: "LA",  # Grayscale with alpha
        6: "RGBA" # RGB with alpha
    }

    mode = color_modes[color_type]
    image = Image.frombytes(mode, (width, height), image_data)

    if color_type == 3:
        image.putpalette(palette)

    image.show()