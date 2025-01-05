import pytest
import os
from parser.__main__ import decode_ihdr, parse_file, main
from unittest.mock import patch

test_images = [
    {
        'file_path': 'examples/kotik_RGB.png',
        'expected_width': 1726,
        'expected_height': 1726,
        'expected_bit_depth': 8,
        'expected_color_type': 2
    },
    {
        'file_path': 'examples/very_small_RGBA.png',
        'expected_width': 1,
        'expected_height': 1,
        'expected_bit_depth': 8,
        'expected_color_type': 6
    },
    {
        'file_path': 'examples/palette.png',
        'expected_width': 393,
        'expected_height': 480,
        'expected_bit_depth': 8,
        'expected_color_type': 3
    },
]


@pytest.mark.parametrize("test_image", test_images)
def test_image_characteristics(test_image):
    file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), test_image['file_path'])
    headers = parse_file(file_path)

    ihdr_chunk = next((h for h in headers if h['Chunk Type'] == 'IHDR'), None)
    assert ihdr_chunk is not None

    ihdr = ihdr_chunk['Data']
    width, height, bit_depth, color_type, _, _, _ = decode_ihdr(ihdr)

    assert width == test_image['expected_width']
    assert height == test_image['expected_height']
    assert bit_depth == test_image['expected_bit_depth']
    assert color_type == test_image['expected_color_type']


@pytest.fixture
def mock_file_path(tmp_path):
    file = tmp_path / "test.png"
    file.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    return str(file)


@pytest.fixture
def mock_parsed_headers():
    return [
        {'Chunk Type': 'IHDR', 'Data': b'\x00\x00\x02\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00', 'CRC': 0, 'Length': 13, 'Data Size': 12},
        {'Chunk Type': 'IDAT', 'Data': b'\x00' * 50, 'CRC': 0, 'Length': 50, 'Data Size': 12},
        {'Chunk Type': 'PLTE', 'Data': b'\x00' * 9, 'CRC': 0, 'Length': 9, 'Data Size': 12},
    ]


def test_file_not_found():
    with patch('builtins.input', return_value='nonexistent_file.png'):
        with pytest.raises(FileNotFoundError):
            main()
