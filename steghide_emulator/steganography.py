import os
import numpy as np
from PIL import Image
import math
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import pandas as pd
from datetime import datetime

# Clean professional styling
sns.set_style("white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12


# -------------------- Helper Functions --------------------
def text_to_binary(text):
    """Converts a string of text into a binary string."""
    return ''.join(format(ord(char), '08b') for char in text)


def binary_to_text(binary):
    """Converts a binary string back into a text string."""
    try:
        if len(binary) % 8 != 0:
            binary = binary.ljust(len(binary) + (8 - len(binary) % 8), '0')
        return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    except (ValueError, IndexError):
        return None


def encrypt_decrypt_xor(message, key):
    """Encrypts or decrypts a message using a simple XOR cipher."""
    encrypted_message = ""
    key_len = len(key)
    for i, char in enumerate(message):
        encrypted_char = chr(ord(char) ^ ord(key[i % key_len]))
        encrypted_message += encrypted_char
    return encrypted_message


# -------------------- LSB Steganography Core --------------------
def hide_message(image_path, secret_message, output_path, encryption_key=""):
    """Hides a secret message within an image using LSB steganography."""
    try:
        image = Image.open(image_path, 'r').convert("RGB")
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
        return None, None
    except Exception as e:
        print(f"Error opening image '{image_path}': {e}")
        return None, None
    
    message_to_hide = secret_message
    if encryption_key:
        message_to_hide = encrypt_decrypt_xor(secret_message, encryption_key)
        print("✓ Message encrypted.")
    
    secret_message_with_delimiter = message_to_hide + "_STOP_"
    binary_message = text_to_binary(secret_message_with_delimiter)
    
    max_bits = image.width * image.height * 3
    if len(binary_message) > max_bits:
        print(f"Error: Message too long. Max capacity: {max_bits} bits.")
        return None, None
    
    pixels = np.array(image, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    
    if len(binary_message) > len(flat_pixels):
        print("Error: Message is too long for the image's pixel count.")
        return None, None
    
    for i, bit in enumerate(binary_message):
        flat_pixels[i] = (flat_pixels[i] & 0b11111110) | int(bit)
    
    stego_pixels = flat_pixels.reshape(pixels.shape)
    stego_image = Image.fromarray(stego_pixels)
    
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        stego_image.save(output_path)
        print(f"✓ Message hidden successfully in {output_path}")
        return np.array(image), np.array(stego_image)
        
    except (ValueError, IOError) as e:
        print(f"Error saving file: {e}")
        return None, None


def reveal_message(image_path, encryption_key=""):
    """Reveals a hidden message from an image using LSB steganography."""
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
    extracted_message = binary_to_text(extracted_binary)
    
    if encryption_key and extracted_message:
        extracted_message = encrypt_decrypt_xor(extracted_message, encryption_key)
    
    return extracted_message


# -------------------- Metrics Calculation --------------------
def calculate_psnr(original_image, stego_image):
    """Calculates the Peak Signal-to-Noise Ratio (PSNR)."""
    if original_image.shape != stego_image.shape:
        print("Error: Images have different dimensions.")
        return None
    
    original_arr = original_image.astype(np.float64)
    stego_arr = stego_image.astype(np.float64)
    
    mse = np.mean((original_arr - stego_arr) ** 2)
    if mse == 0:
        return float('inf')
    
    max_pixel_value = 255.0
    psnr = 20 * math.log10(max_pixel_value / math.sqrt(mse))
    return psnr


def calculate_ber(original_message, extracted_message):
    """Calculates the Bit Error Rate (BER)."""
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


def calculate_mse(original_image, stego_image):
    """Calculate Mean Squared Error."""
    return np.mean((original_image.astype(np.float64) - stego_image.astype(np.float64)) ** 2)


# -------------------- CLEAN DASHBOARD --------------------
def plot_clean_dashboard(original, stego, psnr_value, ber_encrypted, ber_decrypted, 
                        image_name, message_length, output_path="clean_dashboard.png"):
    """
    ULTRA-CLEAN DASHBOARD - No summary panel, only key visualizations
    3 rows, generous spacing, professional layout
    """
    
    # Create figure with generous spacing
    fig = plt.figure(figsize=(20, 11), facecolor='white')
    
    # Define grid with MORE spacing
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(3, 3, figure=fig, 
                  hspace=0.75, wspace=0.50,  # Even more spacing!
                  left=0.08, right=0.94, top=0.90, bottom=0.08)
    
    # Professional color palette
    color_excellent = '#2ecc71'
    color_good = '#f39c12'
    color_poor = '#e74c3c'
    color_blue = '#3498db'
    color_gray = '#7f8c8d'
    
    # Convert images
    if len(original.shape) == 3:
        original_rgb = cv2.cvtColor(original, cv2.COLOR_RGB2BGR)
        stego_rgb = cv2.cvtColor(stego, cv2.COLOR_RGB2BGR)
    else:
        original_rgb = original
        stego_rgb = stego
    
    # Calculate metrics
    mse_value = calculate_mse(original, stego)
    modified_pixels = np.sum(original != stego)
    total_pixels = original.size
    modification_rate = (modified_pixels / total_pixels) * 100
    
    # Quality determination
    quality_color = color_excellent if psnr_value > 40 else color_good if psnr_value > 30 else color_poor
    quality_text = "EXCELLENT" if psnr_value > 40 else "GOOD" if psnr_value > 30 else "POOR"
    
    # ==================== ROW 1: IMAGE COMPARISON ====================
    # Original Image
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(original_rgb)
    ax1.set_title('Original Image', fontsize=16, fontweight='bold', pad=20, color='#34495e')
    ax1.axis('off')
    
    # Stego Image
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(stego_rgb)
    ax2.set_title('Stego Image', fontsize=16, fontweight='bold', pad=20, color=quality_color)
    ax2.axis('off')
    
    # Difference Heatmap
    ax3 = fig.add_subplot(gs[0, 2])
    diff = cv2.absdiff(original, stego)
    diff_amplified = np.clip(diff * 50, 0, 255).astype(np.uint8)
    if len(diff_amplified.shape) == 3:
        diff_gray = cv2.cvtColor(diff_amplified, cv2.COLOR_RGB2GRAY)
    else:
        diff_gray = diff_amplified
    
    im = ax3.imshow(diff_gray, cmap='hot')
    ax3.set_title('Pixel Changes (50x)', fontsize=16, fontweight='bold', pad=20, color='#e74c3c')
    ax3.axis('off')
    
    # Add colorbar below heatmap
    cbar = plt.colorbar(im, ax=ax3, orientation='horizontal', pad=0.08, shrink=0.75)
    cbar.set_label('Intensity', fontsize=12, fontweight='bold')
    
    # ==================== ROW 2: KEY METRICS ====================
    # PSNR Display (Spans 2 columns)
    ax4 = fig.add_subplot(gs[1, 0:2])
    
    # Large number display
    ax4.text(0.5, 0.62, f'{psnr_value:.2f}', 
            ha='center', va='center', fontsize=65, fontweight='bold', color=quality_color,
            transform=ax4.transAxes)
    ax4.text(0.5, 0.36, 'dB', 
            ha='center', va='center', fontsize=24, color=color_gray,
            transform=ax4.transAxes)
    ax4.text(0.5, 0.16, f'PSNR Quality: {quality_text}', 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#34495e',
            transform=ax4.transAxes)
    
    # Add quality indicator bar
    quality_ranges = [0, 30, 40, 100]
    quality_colors = [color_poor, color_good, color_excellent]
    for i in range(3):
        ax4.barh(0, quality_ranges[i+1] - quality_ranges[i], left=quality_ranges[i],
                height=0.08, color=quality_colors[i], alpha=0.35)
    
    # Mark current position
    ax4.plot([psnr_value], [0], 'D', markersize=16, color=quality_color, 
            markeredgecolor='black', markeredgewidth=2.5)
    
    ax4.set_xlim(0, 70)
    ax4.set_ylim(-0.12, 0.12)
    ax4.set_xlabel('PSNR Scale (dB)', fontsize=13, fontweight='bold')
    ax4.set_yticks([])
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_visible(False)
    ax4.grid(axis='x', alpha=0.3, linestyle='--')
    
    # BER Comparison
    ax5 = fig.add_subplot(gs[1, 2])
    
    ber_labels = ['Encrypted', 'Decrypted']
    ber_values = [ber_encrypted, ber_decrypted]
    colors_ber = [color_poor, color_blue]
    
    bars = ax5.bar(ber_labels, ber_values, width=0.6, color=colors_ber, 
                  edgecolor='black', linewidth=2.5, alpha=0.85)
    
    # Add values on top
    for bar, val in zip(bars, ber_values):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.6f}',
                ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax5.set_ylabel('Bit Error Rate', fontsize=13, fontweight='bold')
    ax5.set_title('BER Analysis\n(Lower is Better)', fontsize=16, fontweight='bold', pad=18, color='#34495e')
    ax5.grid(axis='y', alpha=0.3, linestyle='--')
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    ax5.set_ylim(0, max(ber_values) * 1.5 if max(ber_values) > 0 else 0.001)
    
    # ==================== ROW 3: HISTOGRAM ONLY (FULL WIDTH) ====================
    # RGB Histogram (Spans all 3 columns)
    ax7 = fig.add_subplot(gs[2, :])
    
    if len(original.shape) == 3:
        colors_hist = ['#e74c3c', '#2ecc71', '#3498db']
        labels_hist = ['Red', 'Green', 'Blue']
        
        for i, (color, label) in enumerate(zip(colors_hist, labels_hist)):
            hist_orig = cv2.calcHist([original], [i], None, [256], [0, 256])
            hist_stego = cv2.calcHist([stego], [i], None, [256], [0, 256])
            
            ax7.plot(hist_orig, color=color, alpha=0.45, linewidth=2.5, linestyle='-')
            ax7.plot(hist_stego, color=color, alpha=0.9, linewidth=2.5, linestyle='--', label=f'{label}')
    
    ax7.set_xlabel('Pixel Value', fontsize=14, fontweight='bold')
    ax7.set_ylabel('Frequency', fontsize=14, fontweight='bold')
    ax7.set_title('RGB Histogram Comparison (Solid=Original, Dashed=Stego)', 
                  fontsize=17, fontweight='bold', pad=20, color='#34495e')
    ax7.legend(loc='upper right', fontsize=12, framealpha=0.95)
    ax7.grid(alpha=0.3, linestyle='--')
    ax7.set_xlim([0, 256])
    ax7.spines['top'].set_visible(False)
    ax7.spines['right'].set_visible(False)
    
    # Footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.99, 0.02, f'Generated: {timestamp}', 
            ha='right', fontsize=10, style='italic', color='#95a5a6')
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Clean dashboard (no summary) saved: {output_path}")
    plt.show()
    
    return output_path


# -------------------- Main Application --------------------
class LSBSteganography:
    def __init__(self):
        self.original = None
        self.stego_img = None
        self.psnr = None
        self.message = None
        self.encryption_key = None
        self.output_path = None
    
    def embed(self, image_path, message, output_path, encryption_key=""):
        """Embed message and store metadata"""
        self.message = message
        self.encryption_key = encryption_key
        self.output_path = output_path
        
        self.original, self.stego_img = hide_message(image_path, message, output_path, encryption_key)
        
        if self.original is not None and self.stego_img is not None:
            self.psnr = calculate_psnr(self.original, self.stego_img)
            print(f"✓ PSNR: {self.psnr:.2f} dB")
            return True
        return False
    
    def extract(self, image_path, encryption_key=""):
        """Extract message from image"""
        return reveal_message(image_path, encryption_key)
    
    def generate_analysis(self):
        """Generate clean analytics dashboard without summary"""
        if self.original is None or self.stego_img is None:
            print("❌ Error: No embedding data found. Please embed a message first.")
            return None
        
        extracted_encrypted = reveal_message(self.output_path, "")
        extracted_decrypted = reveal_message(self.output_path, self.encryption_key)
        
        if self.encryption_key:
            encrypted_message = encrypt_decrypt_xor(self.message, self.encryption_key)
            ber_encrypted = calculate_ber(encrypted_message, extracted_encrypted)
        else:
            ber_encrypted = calculate_ber(self.message, extracted_encrypted)
        
        ber_decrypted = calculate_ber(self.message, extracted_decrypted)
        
        image_name = os.path.basename(self.output_path)
        plot_clean_dashboard(
            self.original, 
            self.stego_img, 
            self.psnr,
            ber_encrypted,
            ber_decrypted,
            image_name,
            len(self.message)
        )
    
    def export_metrics_csv(self, csv_path="steganography_metrics.csv"):
        """Export metrics to CSV"""
        if self.original is None or self.stego_img is None:
            print("❌ Error: No data to export.")
            return
        
        mse_value = calculate_mse(self.original, self.stego_img)
        modified_pixels = np.sum(self.original != self.stego_img)
        total_pixels = self.original.size
        modification_rate = (modified_pixels / total_pixels) * 100
        
        extracted_encrypted = reveal_message(self.output_path, "")
        extracted_decrypted = reveal_message(self.output_path, self.encryption_key)
        
        if self.encryption_key:
            encrypted_message = encrypt_decrypt_xor(self.message, self.encryption_key)
            ber_encrypted = calculate_ber(encrypted_message, extracted_encrypted)
        else:
            ber_encrypted = calculate_ber(self.message, extracted_encrypted)
        
        ber_decrypted = calculate_ber(self.message, extracted_decrypted)
        
        data = {
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Image_Name': [os.path.basename(self.output_path)],
            'Image_Width': [self.original.shape[1]],
            'Image_Height': [self.original.shape[0]],
            'Message_Length_Bytes': [len(self.message)],
            'PSNR_dB': [self.psnr],
            'MSE': [mse_value],
            'BER_Encrypted': [ber_encrypted],
            'BER_Decrypted': [ber_decrypted],
            'Modification_Rate_Percent': [modification_rate],
            'Capacity_Utilization_Percent': [(len(self.message) * 8 / total_pixels) * 100]
        }
        
        df = pd.DataFrame(data)
        
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
        
        print(f"✅ Metrics exported to: {csv_path}")


# -------------------- Simple Menu --------------------
def main():
    stego = LSBSteganography()
    
    print("\n" + "="*70)
    print("  LSB STEGANOGRAPHY EMULATOR")
    print("="*70 + "\n")
    
    while True:
        print("\nMAIN MENU")
        print("-" * 50)
        print("1. Embed message in image")
        print("2. Extract message from image")
        print("3. Generate clean dashboard")
        print("4. Export metrics to CSV")
        print("5. Exit")
        print("-" * 50)
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            print("\n--- EMBED MESSAGE ---")
            image_path = input("Image path: ").strip()
            if not os.path.exists(image_path):
                print("❌ Image not found!")
                continue
            
            message = input("Secret message: ").strip()
            if not message:
                print("❌ Message cannot be empty!")
                continue
            
            encryption_key = input("Encryption key (optional): ").strip()
            output_path = input("Output path (default: stego_output.png): ").strip() or "stego_output.png"
            
            print("\n⏳ Embedding...")
            if stego.embed(image_path, message, output_path, encryption_key):
                print(f"✅ Saved to: {output_path}")
                
        elif choice == '2':
            print("\n--- EXTRACT MESSAGE ---")
            stego_path = input("Stego image path: ").strip()
            if not os.path.exists(stego_path):
                print("❌ Image not found!")
                continue
            
            encryption_key = input("Decryption key (if used): ").strip()
            
            print("\n⏳ Extracting...")
            extracted = stego.extract(stego_path, encryption_key)
            
            if extracted:
                print(f"\n✅ Message: '{extracted}'")
            else:
                print("❌ Could not extract message.")
                
        elif choice == '3':
            print("\n--- GENERATE CLEAN DASHBOARD ---")
            if stego.original is None:
                print("❌ No data. Embed a message first (Option 1).")
            else:
                print("\n⏳ Generating clean dashboard...")
                stego.generate_analysis()
        
        elif choice == '4':
            print("\n--- EXPORT TO CSV ---")
            if stego.original is None:
                print("❌ No data to export.")
            else:
                csv_name = input("CSV filename (default: steganography_metrics.csv): ").strip()
                csv_name = csv_name or "steganography_metrics.csv"
                print("\n⏳ Exporting...")
                stego.export_metrics_csv(csv_name)
                
        elif choice == '5':
            print("\n" + "="*70)
            print("  Thank you for using LSB Steganography!")
            print("="*70 + "\n")
            break
            
        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    main()