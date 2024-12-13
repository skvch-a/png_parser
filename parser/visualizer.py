from typing import List, Dict

from . import Image
from zlib import decompress


def paeth_predictor(a: int, b: int, c: int) -> int:
    """
        Алгоритм для фильтрации данных в PNG (фильтр 4 типа)

        Args:
            a (int): Значение пикселя слева.
            b (int): Значение пикселя сверху.
            c (int): Значение пикселя сверху слева.

        Returns:
            int: Значение пикселя на основе предсказания.
        """
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


def apply_filtering(data: bytes, width: int, height: int, bytes_per_pixel: int) -> bytes:
    """Применяет фильтрацию к данным изображения"""
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


def visualize(headers: List[Dict[str, any]], width: int, height: int, color_type: int) -> None:
    """Отвечает за попиксельную отрисовку изображения"""
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
        plte_chunk = next((h for h in headers if h['Chunk Type'] == 'PLTE'))
        palette = plte_chunk['Data']
        image.putpalette(palette)
    image.show()