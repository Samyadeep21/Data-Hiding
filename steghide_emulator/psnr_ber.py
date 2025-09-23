import numpy as np
from PIL import Image
import math
import os
import matplotlib.pyplot as plt

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

def encrypt_decrypt_xor(message, key):
    """
    Encrypts or decrypts a message using a simple XOR cipher with a given key.
    """
    encrypted_message = ""
    key_len = len(key)
    for i, char in enumerate(message):
        encrypted_char = chr(ord(char) ^ ord(key[i % key_len]))
        encrypted_message += encrypted_char
    return encrypted_message

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
    
    if len(binary_message) > len(flat_pixels):
        print("Error: Message is too long for the image's pixel count.")
        return
    
    for i, bit in enumerate(binary_message):
        flat_pixels[i] = (flat_pixels[i] & 0b11111110) | int(bit)

    stego_pixels = flat_pixels.reshape(pixels.shape)
    stego_image = Image.fromarray(stego_pixels)
    
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        stego_image.save(output_path)
        print(f"Message hidden successfully in {output_path}")

        log_file = "table.txt"
        header = "Original Image Path | Stego Image Path | Secret Message | Encryption Key\n"
        log_entry = f"{image_path} | {output_path} | {secret_message}\n"
        
        mode = "w" if not os.path.exists(log_file) else "a"
        with open(log_file, mode) as f:
            if mode == "w":
                f.write(header)
                f.write("--- | --- | --- | ---\n")
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
    binary_message = ''.join(str(bit) for bit in (pixels & 1).flatten())
    
    delimiter = "_STOP_"
    binary_delimiter = text_to_binary(delimiter)
    
    if binary_delimiter not in binary_message:
        print("Error: Could not find a hidden message.")
        return None
        
    end_index = binary_message.find(binary_delimiter)
    extracted_binary = binary_message[:end_index]
    
    return binary_to_text(extracted_binary)

def calculate_psnr(original_image_path, stego_image_path):
    """Calculates the Peak Signal-to-Noise Ratio (PSNR) between two images."""
    try:
        original = Image.open(original_image_path).convert("RGB")
        stego = Image.open(stego_image_path).convert("RGB")
    except FileNotFoundError:
        print("Error: One of the image files was not found.")
        return None
    
    original_arr = np.array(original)
    stego_arr = np.array(stego)
    
    if original_arr.shape != stego_arr.shape:
        print("Error: Images have different dimensions.")
        return None
        
    mse = np.mean((original_arr - stego_arr) ** 2)
    if mse == 0:
        return float('inf')
    
    max_pixel_value = 255.0
    psnr = 20 * math.log10(max_pixel_value / math.sqrt(mse))
    return psnr

def calculate_ber(original_message, extracted_message):
    """Calculates the Bit Error Rate (BER) between two strings."""
    if extracted_message is None:
        return 1.0
        
    binary_original = text_to_binary(original_message)
    binary_extracted = text_to_binary(extracted_message)
    
    max_len = max(len(binary_original), len(binary_extracted))
    binary_original = binary_original.ljust(max_len, '0')
    binary_extracted = binary_extracted.ljust(max_len, '0')
    
    error_count = sum(1 for ob, eb in zip(binary_original, binary_extracted) if ob != eb)
    total_bits = len(binary_original)
    
    if total_bits == 0:
        return 0.0
        
    return error_count / total_bits

def plot_results_comparison(psnr_value, ber_encrypted, ber_decrypted, image_name):
    """
    Creates bar charts comparing PSNR, Encrypted BER, and Decrypted BER.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f'Steganography Evaluation for {image_name}')

    # PSNR Bar Chart
    psnr_label = f'{psnr_value:.2f} dB'
    ax1.bar(['PSNR'], [psnr_value], color='green')
    ax1.set_title('PSNR (Higher is Better)')
    ax1.set_ylabel('Decibels (dB)')
    ax1.set_ylim(0, 50)
    ax1.text(0, psnr_value, psnr_label, ha='center', va='bottom')

    # BER Comparison Bar Chart
    labels = ['Encrypted BER', 'Decrypted BER']
    ber_values = [ber_encrypted, ber_decrypted]
    colors = ['red', 'blue']
    ax2.bar(labels, ber_values, color=colors)
    ax2.set_title('BER Comparison (Lower is Better)')
    ax2.set_ylabel('Bit Error Rate')
    ax2.set_ylim(0, 1.0)
    
    for i, v in enumerate(ber_values):
        ax2.text(i, v + 0.02, f'{v:.5f}', ha='center')

    plt.tight_layout()
    plt.show()

# --- Main execution block ---
if __name__ == "__main__":
    mode = input("Do you want to (h)ide or (r)eveal a message? ").lower()
    
    if mode.startswith('h'):
        original_image = input("Enter the path to the original image (e.g., my_image.png): ")
        secret_text = input("Enter the secret message you want to hide: ")
        output_image = input("Enter the output image path (e.g., secret_image.png): ")
        
        encryption_key = input("Enter an encryption key (optional, press Enter to skip): ")
        
        secret_text_to_hide = secret_text
        if encryption_key:
            secret_text_to_hide = encrypt_decrypt_xor(secret_text, encryption_key)
            print("Message encrypted.")
        
        hide_message(original_image, secret_text_to_hide, output_image)
        
        if encryption_key:
            # Update log file with encryption key
            with open("table.txt", "r+") as f:
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                    if line.startswith(original_image):
                        f.write(line.strip() + f" | {encryption_key}\n")
                    else:
                        f.write(line)

    elif mode.startswith('r'):
        stego_image = input("Enter the path to the image with the hidden message: ")
        
        original_img = None
        original_msg = None
        encryption_key = None
        log_file = "table.txt"
        
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    parts = [p.strip() for p in line.strip().split('|')]
                    if len(parts) >= 3 and parts[1] == stego_image:
                        original_img, _, original_msg = parts[:3]
                        if len(parts) > 3:
                            encryption_key = parts[3]
                        print(f"\n✅ Record found in {log_file}!")
                        break
        
        if original_img is None:
            print(f"\nℹ️ No record found for '{stego_image}'. Please enter details manually.")
            original_img = input("Enter the path to the ORIGINAL image: ")
            original_msg = input("Enter the ORIGINAL secret message that was hidden: ")
            encryption_key = input("Enter the encryption key used (if any, press Enter to skip): ")
        
        print("\nCalculating PSNR...")
        psnr_value = calculate_psnr(original_img, stego_image)
        if psnr_value is not None:
            if psnr_value == float('inf'):
                print("   PSNR Result: Infinite (The images are identical).")
            else:
                print(f"   PSNR Result: {psnr_value:.2f} dB (Higher is better)")
        
        print("\nCalculating BER...")
        extracted_message = reveal_message(stego_image)
        
        decrypted_message = None
        if extracted_message is not None:
            if encryption_key:
                decrypted_message = encrypt_decrypt_xor(extracted_message, encryption_key)
                print(f"   Decrypted message: '{decrypted_message}'")
            else:
                decrypted_message = extracted_message
                print(f"   Extracted message: '{decrypted_message}'")
        else:
            print("   Could not extract a message.")

        # Recalculate BER for the original text vs the extracted decrypted text
        ber_value_decrypted = calculate_ber(original_msg, decrypted_message)
        
        # Calculate BER for the binary messages (original vs extracted)
        original_binary_to_hide = text_to_binary(original_msg)
        if encryption_key:
            original_binary_to_hide = text_to_binary(encrypt_decrypt_xor(original_msg, encryption_key))
            
        extracted_binary_from_stego = text_to_binary(extracted_message)
        ber_value_encrypted = calculate_ber(original_binary_to_hide, extracted_binary_from_stego)
        
        print(f"   BER for ENCRYPTED message: {ber_value_encrypted:.5f}")
        print(f"   BER for DECRYPTED message: {ber_value_decrypted:.5f}")
        
        image_name = os.path.basename(stego_image)
        plot_results_comparison(psnr_value, ber_value_encrypted, ber_value_decrypted, image_name)
        
    else:
        print("Invalid mode selected. Please choose 'hide' or 'reveal'.")