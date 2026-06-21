import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from cryptography.fernet import Fernet
import base64
import hashlib
import math
import random


FERNET_PASSWORD = "anime_stego_secret_password"


def get_fernet_key():
    key = hashlib.sha256(FERNET_PASSWORD.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_message(message):
    fernet = Fernet(get_fernet_key())
    return fernet.encrypt(message.encode("utf-8")).decode("utf-8")


def decrypt_message(encrypted_message):
    fernet = Fernet(get_fernet_key())
    return fernet.decrypt(encrypted_message.encode("utf-8")).decode("utf-8")


def message_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode("utf-8"))


def binary_to_message(binary_data):
    bytes_list = []

    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]

        if len(byte) == 8:
            bytes_list.append(int(byte, 2))

    return bytes(bytes_list).decode("utf-8")


def get_edge_positions(image_array):
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200)

    positions = []
    height, width = edges.shape

    for y in range(height):
        for x in range(width):
            if edges[y, x] > 0:
                positions.append((y, x))

    return positions


def get_shuffled_positions(positions, secret_key):
    seed = int(hashlib.sha256(secret_key.encode()).hexdigest(), 16)

    rng = random.Random(seed)
    shuffled = positions.copy()
    rng.shuffle(shuffled)

    return shuffled


def encode_fusion_stego(image_path, encrypted_message, output_path, secret_key):
    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)

    message_binary = message_to_binary(encrypted_message)

    length_header = format(len(message_binary), "032b")
    final_binary = length_header + message_binary

    edge_positions = get_edge_positions(image_array)

    if len(final_binary) > len(edge_positions):
        raise ValueError(
            "Message is too large for edge-based embedding in this image. "
            "Use a bigger image or shorter message."
        )

    shuffled_positions = get_shuffled_positions(edge_positions, secret_key)

    for bit_index, bit in enumerate(final_binary):
        y, x = shuffled_positions[bit_index]

        pixel = image_array[y, x]
        pixel[2] = (pixel[2] & 254) | int(bit)
        image_array[y, x] = pixel

    encoded_image = Image.fromarray(image_array.astype(np.uint8))
    encoded_image.save(output_path)

    return output_path


def decode_fusion_stego(image_path, secret_key):
    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)

    edge_positions = get_edge_positions(image_array)
    shuffled_positions = get_shuffled_positions(edge_positions, secret_key)

    if len(shuffled_positions) < 32:
        raise ValueError("Image does not contain enough edge data.")

    length_bits = ""

    for i in range(32):
        y, x = shuffled_positions[i]
        pixel = image_array[y, x]
        length_bits += str(pixel[2] & 1)

    message_length = int(length_bits, 2)

    if message_length <= 0 or message_length > len(shuffled_positions) - 32:
        raise ValueError("Wrong secret key or corrupted image.")

    message_bits = ""

    for i in range(32, 32 + message_length):
        y, x = shuffled_positions[i]
        pixel = image_array[y, x]
        message_bits += str(pixel[2] & 1)

    return binary_to_message(message_bits)


def calculate_mse(original_path, encoded_path):
    original = cv2.imread(original_path)
    encoded = cv2.imread(encoded_path)

    original = cv2.resize(original, (encoded.shape[1], encoded.shape[0]))

    mse = np.mean((original - encoded) ** 2)
    return float(mse)


def calculate_psnr(mse):
    if mse == 0:
        return 100

    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

    return float(psnr)


def calculate_ssim(original_path, encoded_path):
    original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    encoded = cv2.imread(encoded_path, cv2.IMREAD_GRAYSCALE)

    original = cv2.resize(original, (encoded.shape[1], encoded.shape[0]))

    value = ssim(original, encoded)
    return float(value)


def generate_histogram(image_path, output_path):
    image = cv2.imread(image_path)

    hist_img = np.zeros((300, 512, 3), dtype=np.uint8)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, 300, cv2.NORM_MINMAX)

        for x in range(1, 256):
            cv2.line(
                hist_img,
                (x * 2, 300 - int(hist[x - 1])),
                (x * 2, 300 - int(hist[x])),
                color,
                1
            )

    cv2.imwrite(output_path, hist_img)
    return output_path