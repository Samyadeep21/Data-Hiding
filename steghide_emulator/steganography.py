import numpy as np
from PIL import Image
import math
import os

# --- Helper functions ---
def text_to_binary(text):
    """Converts a string of text into a binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    """Converts a binary string back into a text string."""
    try:
        # Pad the binary string to be a multiple of 8
        if len(binary) % 8 != 0:
            binary = binary.ljust(len(binary) + (8 - len(binary) % 8), '0')
        return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    except (ValueError, IndexError):
        return None

# --- Main Functions (optimized and refactored) ---
def hide_message(image_path, secret_message, output_path):
    """
    Hides a secret message within an image using NumPy for performance.
    """
    try:
        image = Image.open(image_path, 'r').convert("RGB")
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
        return
    except Exception as e:
        print(f"Error opening image '{image_path}': {e}")
        return

    secret_message_with_delimiter = secret_message + "_STOP_"
    binary_message = text_to_binary(secret_message_with_delimiter)

    max_bits = image.width * image.height * 3
    if len(binary_message) > max_bits:
        print(f"Error: The message is too long to be hidden. "
              f"Max capacity: {max_bits} bits.")
        return

    pixels = np.array(image, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    
    # Check if the message is larger than the number of pixels
    if len(binary_message) > len(flat_pixels):
        print("Error: Message is too long for the image's pixel count.")
        return
    
    # Efficiently embed the binary message bits into the LSB of pixels
    # This loop is much faster than the original pixel.load() iteration
    for i, bit in enumerate(binary_message):
        flat_pixels[i] = (flat_pixels[i] & 0b11111110) | int(bit)

    stego_pixels = flat_pixels.reshape(pixels.shape)
    stego_image = Image.fromarray(stego_pixels)
    
    # Get the directory from the output path
    output_dir = os.path.dirname(output_path)

    # Create the directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        stego_image.save(output_path)
        print(f"Message hidden successfully in {output_path}")

        log_file = "table.txt"
        header = "Original Image Path | Stego Image Path | Secret Message\n"
        log_entry = f"{image_path} | {output_path} | {secret_message}\n"
        
        mode = "w" if not os.path.exists(log_file) else "a"
        with open(log_file, mode) as f:
            if mode == "w":
                f.write(header)
                f.write("--- | --- | ---\n")
            f.write(log_entry)
        
        print(f"Details logged to {log_file}")
    
    except (ValueError, IOError) as e:
        print(f"Error saving file: {e}. Please ensure the output path is a valid filename.")

def reveal_message(image_path):
    """
    Reveals a hidden message from an image using LSB steganography.
    This version uses vectorized NumPy operations for speed.
    """
    try:
        image = Image.open(image_path, 'r').convert("RGB")
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
        return None
    except Exception as e:
        print(f"Error opening image '{image_path}': {e}")
        return None
    
    pixels = np.array(image)
    
    # Vectorized extraction of LSBs from all color channels
    binary_message = ''.join(str(bit) for bit in (pixels & 1).flatten())
    
    delimiter = "_STOP_"
    binary_delimiter = text_to_binary(delimiter)
    
    if binary_delimiter not in binary_message:
        print("Error: Could not find a hidden message.")
        return None
        
    end_index = binary_message.find(binary_delimiter)
    extracted_binary = binary_message[:end_index]
    
    return binary_to_text(extracted_binary)

# --- Main execution block ---
if __name__ == "__main__":
    mode = input("Do you want to (h)ide or (r)eveal a message? ").lower()
    if mode.startswith('h'):
        original_image = input("Enter the path to the original image (e.g., my_image.png): ")
        secret_text = input("Enter the secret message you want to hide: ")
        output_image = input("Enter the output image path (e.g., secret_image.png): ")
        hide_message(original_image, secret_text, output_image)
    elif mode.startswith('r'):
        stego_image = input("Enter the path to the image with the hidden message: ")
        revealed_text = reveal_message(stego_image)
        if revealed_text is not None:
            print(f"The hidden message is: {revealed_text}")
    else:
        print("Invalid mode selected. Please choose 'hide' or 'reveal'.")