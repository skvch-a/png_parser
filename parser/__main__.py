import struct
import os
import zlib

from . import CAN_VISUALIZE
from .visualizer import visualize
from .print_utils import print_title, print_line, print_headers, print_palette, print_decoded_ihdr
from .filtering import apply_filtering
from .histograms import create_histograms

from typing import List, Dict, BinaryIO, Tuple
from sys import argv


def parse_file(file_path: str) -> List[Dict[str, any]]:
    """Извлекает все заголовки из PNG файла"""
    headers = []
    with open(file_path, 'rb') as file:
        signature = file.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise Exception("Это не PNG файл")

        while True:
            try:
                header = parse_header(file)
            except:
                raise Exception('Обязательный чанк отсутствует/поврежден')

            headers.append(header)
            if header['Chunk Type'] == 'IEND':
                break
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


def decode_ihdr(ihdr_chunk_data: bytes) -> Tuple[int, int, int, int, str, str, str]:
    """Извлекает данные из заголовка IHDR"""
    try:
        width, height = struct.unpack('>II', ihdr_chunk_data[:8])
        bit_depth = ihdr_chunk_data[8]
        color_type = ihdr_chunk_data[9]
        compression_method = 'DEFLATE' if ihdr_chunk_data[10] == 0 else 'Неизвестный'
        filter_method = 'Adaptive' if ihdr_chunk_data[11] == 0 else 'Неизвестный'
        if ihdr_chunk_data[12] == 0:
            interlace_method = 'Отсутствует'
        elif ihdr_chunk_data[12] == 1:
            interlace_method = 'Adam7'
        else:
            interlace_method = 'Неизвестный'
        if 'Неизвестный' in (compression_method, filter_method, interlace_method):
            print('ПРЕДУПРЕЖДЕНИЕ: Обнаружены неизвестные методы в IHDR. Изображение обработано методами по умолчанию')
            print_line()
        return width, height, bit_depth, color_type, compression_method, filter_method, interlace_method
    except Exception:
        raise Exception('Некорректный IHDR')


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
        width, height, bit_depth, color_type, compression_method, filter_method, interlace_method = decode_ihdr(ihdr)
        print_decoded_ihdr(width, height, bit_depth, color_type, compression_method, filter_method, interlace_method)

        palette = None
        if plte_chunk:
            palette = plte_chunk['Data']
            print_palette(palette)


        print_headers(headers)
        idat_data = b''.join(h['Data'] for h in headers if h['Chunk Type'] == 'IDAT')
        try:
            decompressed_idat_data = zlib.decompress(idat_data)
        except zlib.error as exception:
            if str(exception) == "Error -3 while decompressing data: incorrect header check":
                message = "Некорректная контрольная сумма заголовка в IDAT"
            else:
                message = f"Не удалось разжать IDAT"
            raise Exception(message)

        image_data = apply_filtering(decompressed_idat_data, width, height, color_type)

        if CAN_VISUALIZE:
            visualize(image_data, width, height, color_type, palette)

        create_histograms(image_data, width, height, color_type)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print_line()
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        pass