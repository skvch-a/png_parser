from . import Image
from zlib import decompress


def visualize(headers, width, height, color_type):
    color_modes = {
        0: ("L", 1),  # Grayscale
        2: ("RGB", 3),  # RGB
        3: ("P", 1),  # Indexed-color
        4: ("LA", 2),  # Grayscale with alpha
        6: ("RGBA", 4)  # RGB with alpha
    }

    mode, bytes_per_pixel = color_modes[color_type]
    idat_data = b''.join(h['Data'] for h in headers if h['Chunk Type'] == 'IDAT')
    decompressed_data = decompress(idat_data)

    stride = width * bytes_per_pixel + 1
    raw_pixels = []

    palette = None
    if color_type == 3:
        plte_chunk = next((h for h in headers if h['Chunk Type'] == 'PLTE'), None)
        palette = plte_chunk['Data']

    for y in range(height):
        row_start = y * stride
        row_data = decompressed_data[row_start + 1:row_start + stride]
        raw_pixels.append(row_data)

    image_data = b''.join(raw_pixels)
    image = Image.frombytes(mode, (width, height), image_data)
    if color_type == 3:
        image.putpalette(palette)
    image.show()