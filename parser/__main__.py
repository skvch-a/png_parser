import struct
from PIL import Image
import os


def read_png_headers(file_path):
    headers = []
    try:
        with open(file_path, 'rb') as file:
            signature = file.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Это не PNG файл.")

            while True:
                # Длина данных
                length_data = file.read(4)
                if len(length_data) < 4:
                    break
                length = struct.unpack('>I', length_data)[0]

                # Тип заголовка
                chunk_type = file.read(4).decode('ascii')

                # Данные заголовка
                data = file.read(length)

                # CRC заголовка
                crc_data = file.read(4)
                crc = struct.unpack('>I', crc_data)[0]

                # Добавляем информацию о заголовке
                headers.append({
                    'Chunk Type': chunk_type,
                    'Length': length,
                    'CRC': crc,
                    'Data Size': len(data),
                    'Data': data
                })

                if chunk_type == 'IEND':
                    break
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    return headers


def print_headers(headers):
    print(f"{'Chunk Type':<12} {'Length':<8} {'CRC':<12} {'Data Size':<12}")
    print("-" * 50)
    for header in headers:
        print(f"{header['Chunk Type']:<12} {header['Length']:<8} {header['CRC']:<12} {header['Data Size']:<12}")


def decode_IHDR(data):
    # IHDR заголовок содержит информацию о изображении
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

    print("\nИнформация о заголовке IHDR:")
    print(f"Ширина: {width} пикселей")
    print(f"Высота: {height} пикселей")
    print(f"Глубина цвета: {bit_depth}")
    print(f"Тип цвета: {color_types.get(color_type, 'Неизвестный тип')}")

def decode_PLTE(data):
    print(f"Размер палитры: {len(data) // 3} цветов")

def show_png_image(file_path):
    try:
        image = Image.open(file_path)
        image.show()  # Отображаем изображение с использованием PIL
    except Exception as e:
        print(f"Ошибка при отображении изображения: {e}")


def main():
    file_path = input("Введите путь к файлу: ").strip()

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    print(f"\nИмя файла: {file_name}")
    print(f"Размер файла: {file_size} байт")

    headers = read_png_headers(file_path)
    if headers:
        print("Заголовки PNG файла:")
        print_headers(headers)

        for header in headers:
            chunk_type = header['Chunk Type']
            data = header['Data']
            if chunk_type == 'IHDR':
                decode_IHDR(data)
            elif chunk_type == 'PLTE':
                decode_PLTE(data)

        show_png_image(file_path)


if __name__ == '__main__':
    main()