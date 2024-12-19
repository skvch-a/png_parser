import matplotlib.pyplot as plt
import numpy as np

from .utils import get_bytes_per_pixel


def calculate_histograms(image_data: bytes, width: int, height: int, color_type: int):
    bytes_per_pixel = get_bytes_per_pixel(color_type)
    image_array = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width, bytes_per_pixel))

    red_hist = np.zeros(256, dtype=np.int32)
    green_hist = np.zeros(256, dtype=np.int32)
    blue_hist = np.zeros(256, dtype=np.int32)

    if color_type in (2, 6):
        red_hist = np.bincount(image_array[:, :, 0].flatten(), minlength=256)
        green_hist = np.bincount(image_array[:, :, 1].flatten(), minlength=256)
        blue_hist = np.bincount(image_array[:, :, 2].flatten(), minlength=256)
        total_hist = (red_hist + green_hist + blue_hist) / 3
    else:
        total_hist = np.bincount(image_array.flatten(), minlength=256)

    return total_hist, red_hist, green_hist, blue_hist


def create_histograms(image_data: bytes, width: int, height: int, color_type: int):
    total_hist, red_hist, green_hist, blue_hist = calculate_histograms(image_data, width, height, color_type)

    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.bar(range(256), total_hist, color='gray')
    plt.title("Общая гистограмма")
    plt.xlabel("Яркость")
    plt.ylabel("Количество пикселей")

    if color_type in (2, 6):
        plt.subplot(2, 1, 2)
        plt.bar(range(256), red_hist, color='red', alpha=0.6, label='Красный')
        plt.bar(range(256), green_hist, color='green', alpha=0.6, label='Зеленый')
        plt.bar(range(256), blue_hist, color='blue', alpha=0.6, label='Синий')
        plt.title("Поканальная гистограмма")
        plt.xlabel("Яркость")
        plt.ylabel("Количество пикселей")
        plt.legend()

    plt.tight_layout()
    plt.show()