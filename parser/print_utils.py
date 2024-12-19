def print_line():
    print('-' * 100)


def print_title():
    print('=' * 100)
    print('PNG Parser')
    print('=' * 100)


def print_headers(headers):
    print_line()
    print(f"{'Chunk Type':<12} {'Length':<8} {'CRC':<12} {'Data Size':<12}")
    print_line()
    for header in headers:
        print(f"{header['Chunk Type']:<12} {header['Length']:<8} {header['CRC']:<12} {header['Data Size']:<12}")


def print_decoded_ihdr(width, height, bit_depth, color_type, compression_method, interlace_method):
    color_types = {
        0: "Grayscale",
        2: "RGB",
        3: "Indexed Color",
        4: "Grayscale with Alpha",
        6: "RGBA"
    }

    print(f"Ширина: {width} пикселей")
    print(f"Высота: {height} пикселей")
    print(f"Глубина цвета: {bit_depth}")
    print(f"Тип цвета: {color_types.get(color_type, 'Неизвестный')}")
    print(f"Метод сжатия: {compression_method}")
    print(f"Метод интерлейса: {interlace_method}")


def print_palette(palette):
    print(f"Размер палитры: {len(palette) // 3} цветов")
    colors = []
    for i in range(0, len(palette), 3):
        r, g, b = palette[i:i + 3]
        colors.append(f"({r}, {g}, {b})")

    print_line()
    print("Цвета в палитре:")
    print_line()
    k = 1
    for color in colors:
        print(f'{k}. {color}')
        k += 1