import struct
import os

from . import CAN_VISUALIZE
from .visualizer import visualize
from .print_utils import print_title, print_line, print_headers, print_palette, print_decoded_ihdr
from .filtering import apply_filtering
from .histograms import create_histograms

from typing import List, Dict, BinaryIO, Tuple
from zlib import decompress
from sys import argv


def parse_file(file_path: str) -> List[Dict[str, any]]:
    """Извлекает все заголовки из PNG файла"""
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


def parse_header(file: BinaryIO) -> Dict[str, any]:
    """Извлекает один заголовок из PNG файла"""
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


def decode_ihdr(ihdr_chunk_data: bytes) -> Tuple[int, int, int, int, str, str]:
    """Извлекает данные из заголовка IHDR"""
    width, height = struct.unpack('>II', ihdr_chunk_data[:8])
    bit_depth = ihdr_chunk_data[8]
    color_type = ihdr_chunk_data[9]
    compression_method = 'DEFLATE' if ihdr_chunk_data[10] == 0 else 'Неизвестный'
    interlace_method = 'Adam7' if ihdr_chunk_data[12] == 1 else 'Отсутствует'
    return width, height, bit_depth, color_type, compression_method, interlace_method


def main():
    print_title()

    if len(argv) > 1:
        file_path = argv[1]
    else:
        file_path = input("Введите путь к файлу: ").strip()
        print_line()


    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    print(f"Имя файла: {file_name}")
    print(f"Размер файла: {file_size} байт")
    print_line()

    headers = parse_file(file_path)
    if headers:
        ihdr_chunk = next((h for h in headers if h['Chunk Type'] == 'IHDR'))
        plte_chunk = next((h for h in headers if h['Chunk Type'] == 'PLTE'), None)
        ihdr = ihdr_chunk['Data']
        width, height, bit_depth, color_type, compression_method, interlace_method = decode_ihdr(ihdr)
        print_decoded_ihdr(width, height, bit_depth, color_type, compression_method, interlace_method)

        palette = None
        if plte_chunk:
            palette = plte_chunk['Data']
            print_palette(palette)


        print_headers(headers)
        idat_data = b''.join(h['Data'] for h in headers if h['Chunk Type'] == 'IDAT')
        decompressed_idat_data = decompress(idat_data)
        image_data = apply_filtering(decompressed_idat_data, width, height, color_type)

        if CAN_VISUALIZE:
            visualize(image_data, width, height, color_type, palette)

        create_histograms(image_data, width, height, color_type)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print_line()
        print(f"Произошла ошибка: {e}")