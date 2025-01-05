from unittest.mock import patch
from parser.print_utils import (
    print_line,
    print_title,
    print_headers,
    print_decoded_ihdr,
    print_palette,
)

def test_print_line():
    with patch('builtins.print') as mock_print:
        print_line()
        mock_print.assert_called_once_with('-' * 100)

def test_print_title():
    expected_calls = [
        (('=' * 100),),
        ('PNG Parser',),
        (('=' * 100),),
    ]
    with patch('builtins.print') as mock_print:
        print_title()
        actual_calls = [call.args for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

def test_print_headers():
    headers = [
        {'Chunk Type': 'IHDR', 'Length': 13, 'CRC': 'CRC1', 'Data Size': 13},
        {'Chunk Type': 'IDAT', 'Length': 1000, 'CRC': 'CRC2', 'Data Size': 1000},
    ]
    expected_calls = [
        (('-' * 100),),
        (f"{'Chunk Type':<12} {'Length':<8} {'CRC':<12} {'Data Size':<12}",),
        (('-' * 100),),
        ('IHDR         13       CRC1         13          ',),
        ('IDAT         1000     CRC2         1000        ',),
    ]
    with patch('builtins.print') as mock_print:
        print_headers(headers)
        actual_calls = [call.args for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

def test_print_decoded_ihdr():
    width, height, bit_depth = 512, 256, 8
    color_type, compression_method, filter_method, interlace_method = 6, 0, 0, 0
    expected_calls = [
        ('Ширина: 512 пикселей',),
        ('Высота: 256 пикселей',),
        ('Глубина цвета: 8',),
        ('Тип цвета: RGBA',),
        ('Метод сжатия: 0',),
        ('Метод фильтрации: 0',),
        ('Метод интерлейса: 0',)
    ]
    with patch('builtins.print') as mock_print:
        print_decoded_ihdr(width, height, bit_depth, color_type, compression_method, filter_method, interlace_method)
        actual_calls = [call.args for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

def test_print_decoded_plte():
    plte_chunk_data = bytes([255, 0, 0, 0, 255, 0, 0, 0, 255])
    expected_calls = [
        ('Размер палитры: 3 цветов',),
        (('-' * 100),),
        ('Цвета в палитре:',),
        (('-' * 100),),
        ('1. (255, 0, 0)',),
        ('2. (0, 255, 0)',),
        ('3. (0, 0, 255)',),
    ]
    with patch('builtins.print') as mock_print:
        print_palette(plte_chunk_data)
        actual_calls = [call.args for call in mock_print.call_args_list]
        assert actual_calls == expected_calls