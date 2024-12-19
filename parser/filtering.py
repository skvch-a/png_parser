from .utils import get_bytes_per_pixel


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


def apply_filtering(data: bytes, width: int, height: int, color_type: int) -> bytes:
    """Применяет фильтрацию к данным изображения"""
    bytes_per_pixel = get_bytes_per_pixel(color_type)
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
