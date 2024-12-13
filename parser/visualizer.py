from . import Image
from zlib import decompress


def paeth_predictor(a, b, c):
    """Paeth filter predictor."""
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c


def apply_filtering(data, width, height, bytes_per_pixel):
    """Обрабатывает фильтры PNG."""
    stride = width * bytes_per_pixel
    result = []
    prev_row = bytearray(stride)

    for y in range(height):
        filter_type = data[y * (stride + 1)]
        row_data = bytearray(data[y * (stride + 1) + 1: y * (stride + 1) + 1 + stride])

        if filter_type == 1:
            for i in range(bytes_per_pixel, stride):
                row_data[i] = (row_data[i] + row_data[i - bytes_per_pixel]) % 256

        elif filter_type == 2:
            for i in range(stride):
                row_data[i] = (row_data[i] + prev_row[i]) % 256

        elif filter_type == 3:
            for i in range(stride):
                left = row_data[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
                above = prev_row[i]
                row_data[i] = (row_data[i] + (left + above) // 2) % 256

        elif filter_type == 4:
            for i in range(stride):
                left = row_data[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
                above = prev_row[i]
                upper_left = prev_row[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
                row_data[i] = (row_data[i] + paeth_predictor(left, above, upper_left)) % 256

        result.extend(row_data)
        prev_row = row_data

    return bytes(result)


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

    filtered_data = apply_filtering(decompressed_data, width, height, bytes_per_pixel)

    image = Image.frombytes(mode, (width, height), filtered_data)
    if color_type == 3:
        plte_chunk = next((h for h in headers if h['Chunk Type'] == 'PLTE'), None)
        palette = plte_chunk['Data']
        image.putpalette(palette)
    image.show()