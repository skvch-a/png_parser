def get_bytes_per_pixel(color_type: int):
    color_modes = {
        0: 1,  # Grayscale
        2: 3,  # RGB
        3: 1,  # Indexed-color
        4: 2,  # Grayscale with alpha
        6: 4   # RGB with alpha
    }

    return color_modes[color_type]