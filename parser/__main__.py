import struct
import os

try:
    from PIL import Image
    CAN_VISUALIZE = True
except ImportError:
    CAN_VISUALIZE = False


def parse_file(file_path):
    headers = []
    try:
        with open(file_path, 'rb') as file:
            signature = file.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Это не PNG файл")

            while True:
                header = parse_header(file)
                headers.append(header)
                if header['Chunk Type'] == 'IEND':
                    break
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    return headers


def parse_header(file):
    length = struct.unpack('>I', file.read(4))[0]
    chunk_type = file.read(4).decode('ascii')
    data = file.read(length)
    crc = struct.unpack('>I', file.read(4))[0]
    return {
        'Chunk Type': chunk_type,
        'Length': length,
        'CRC': crc,
        'Data Size': len(data),
        'Data': data
    }


def print_headers(headers):
    print('-' * 100)
    print(f"{'Chunk Type':<12} {'Length':<8} {'CRC':<12} {'Data Size':<12}")
    print("-" * 100)
    for header in headers:
        print(f"{header['Chunk Type']:<12} {header['Length']:<8} {header['CRC']:<12} {header['Data Size']:<12}")


def print_decoded_ihdr(data):
    width, height = struct.unpack('>II', data[:8])
    bit_depth = data[8]
    color_type = data[9]

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
    print(f"Тип цвета: {color_types.get(color_type, 'Неизвестный тип')}")


def print_decoded_plte(data):
    print(f"Размер палитры: {len(data) // 3} цветов")


def main():
    print('=' * 100)
    print('PNG Parser')
    print('=' * 100)

    file_path = input("Введите путь к файлу: ").strip()
    print('-' * 100)

    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
    except FileNotFoundError:
        print('Файл не найден')
        exit()

    print(f"Имя файла: {file_name}")
    print(f"Размер файла: {file_size} байт")
    print('-' * 100)

    headers = parse_file(file_path)
    if headers:
        for header in headers:
            chunk_type = header['Chunk Type']
            data = header['Data']
            if chunk_type == 'IHDR':
                print_decoded_ihdr(data)
            elif chunk_type == 'PLTE':
                print_decoded_plte(data)

        print_headers(headers)
        if CAN_VISUALIZE:
            Image.open(file_path).show()


if __name__ == '__main__':
    main()