import os
from utils.file_analysis import (
    get_file_metadata, extract_strings, analyze_file_structure,
    calculate_entropy, get_byte_frequency, get_hex_dump, run_zsteg
)
from utils.stego_detector import analyze_image_for_steganography
import json

# File to analyze
image_path = 'test_image.png'

print(f"====================== ANALYZING {image_path} =======================")

# Run the basic analysis
print("\n=== BASIC FILE INFO ===")
file_size = os.path.getsize(image_path)
file_type = image_path.split('.')[-1].lower()
entropy_value = calculate_entropy(image_path)

print(f"File Size: {file_size} bytes")
print(f"File Type: {file_type.upper()}")
print(f"Entropy: {entropy_value:.4f}")

# Get metadata
print("\n=== METADATA ===")
metadata = get_file_metadata(image_path)
for key, value in metadata.items():
    print(f"{key}: {value}")

# Run steganography detection
print("\n=== STEGANOGRAPHY DETECTION ===")
detection_result = analyze_image_for_steganography(image_path)
likelihood = detection_result.likelihood
likelihood_percentage = f"{likelihood*100:.1f}%"

print(f"Steganography Likelihood: {likelihood_percentage}")
print(f"Main Finding: {detection_result.main_finding}")

print("\n=== DETECTION INDICATORS ===")
for name, details in detection_result.indicators.items():
    value = details["value"]
    weight = details["weight"]
    print(f"{name.replace('_', ' ').title()}: {value:.3f} (weight: {weight:.1f})")

print("\n=== ANALYSIS EXPLANATION ===")
print(detection_result.explanation)

# Run ZSTEG for PNG files
if file_type.lower() == 'png':
    print("\n=== ZSTEG ANALYSIS ===")
    zsteg_output = run_zsteg(image_path)
    print(zsteg_output)

# Get strings
print("\n=== STRINGS (first 10) ===")
strings = extract_strings(image_path)
for s in strings[:10]:
    print(s)

print("\n=== ANALYSIS COMPLETE ===")