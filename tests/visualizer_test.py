import os

import pytest
from parser.__main__ import parse_file, decode_ihdr
from parser.visualizer import visualize
from parser.filtering import apply_filtering, paeth_predictor
from unittest.mock import patch


def test_visualize():
    file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'examples/palette.png')
    headers = parse_file(file_path)

    ihdr_chunk = next((h for h in headers if h['Chunk Type'] == 'IHDR'), None)
    ihdr = ihdr_chunk['Data']
    width, height, bit_depth, color_type, _, _ = decode_ihdr(ihdr)

    with patch('PIL.Image.Image.show') as mock_show:
        visualize(headers, width, height, color_type)
        mock_show.assert_called_once()


@pytest.mark.parametrize("a, b, c, expected", [
    (0, 0, 0, 0),
    (100, 50, 75, 75),
    (10, 20, 30, 10),
    (200, 150, 100, 200),
])
def test_paeth_predictor(a, b, c, expected):
    assert paeth_predictor(a, b, c) == expected


def test_apply_filtering_filter_type_1():
    data = bytes([1] + [10, 20, 30, 40, 50, 60, 70, 80])
    width = 4
    height = 2
    bytes_per_pixel = 1
    result = apply_filtering(data, width, height, bytes_per_pixel)
    assert result == b'\n\x1e<d<FP'

def test_apply_filtering_filter_type_2():
    data = bytes([2] + [10, 20, 30, 40] + [2] + [50, 60, 70, 80])
    width = 4
    height = 2
    bytes_per_pixel = 1
    result = apply_filtering(data, width, height, bytes_per_pixel)
    assert result == bytes([10, 20, 30, 40, 60, 80, 100, 120])

def test_apply_filtering_filter_type_3():
    data = bytes([3] + [10, 20, 30, 40] + [3] + [50, 60, 70, 80])
    width = 4
    height = 2
    bytes_per_pixel = 1
    result = apply_filtering(data, width, height, bytes_per_pixel)
    assert result == b'\n\x19*=7d\x8d\xb5'

def test_apply_filtering_filter_type_4():
    data = bytes([4] + [10, 20, 30, 40] + [4] + [50, 60, 70, 80])
    width = 4
    height = 2
    bytes_per_pixel = 1
    result = apply_filtering(data, width, height, bytes_per_pixel)
    assert result == b'\n\x1e<d<x\xbe\x0e'
