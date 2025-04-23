"""
Steganography brute-force decoder utilities.
Provides automated capabilities for detecting and extracting hidden data from images.
"""

import os
import re
import io
import subprocess
import tempfile
import binascii
from PIL import Image
import numpy as np
import base64
from pathlib import Path
import json

class DecoderResult:
    """Container for storing decoder results."""
    def __init__(self, method, data=None, success=False, confidence=0.0, info=None):
        self.method = method  # Decoding method used
        self.data = data      # Extracted data (if any)
        self.success = success  # Whether decoding was successful
        self.confidence = confidence  # How confident are we in the result (0-1)
        self.info = info or {}  # Additional information about the result
    
    def to_dict(self):
        """Convert result to dictionary."""
        return {
            "method": self.method,
            "success": self.success,
            "confidence": self.confidence,
            "info": self.info,
            "data_preview": str(self.data)[:100] if self.data else None,
            "data_size": len(self.data) if self.data else 0
        }
    
    def __repr__(self):
        return f"DecoderResult(method={self.method}, success={self.success}, confidence={self.confidence:.2f})"

# LSB (Least Significant Bit) Decoders
def decode_lsb(image_path, bit_plane=0, channel=0):
    """
    Extract data hidden using LSB steganography.
    
    Args:
        image_path: Path to the image file
        bit_plane: Which bit plane to extract (0=least significant, 7=most significant)
        channel: Which color channel to use (0=R, 1=G, 2=B, 3=Alpha)
    
    Returns:
        DecoderResult object
    """
    try:
        # Open the image
        img = Image.open(image_path)
        if img.mode != 'RGB' and img.mode != 'RGBA':
            img = img.convert('RGB')
        
        # Convert to numpy array for easier manipulation
        pixels = np.array(img)
        
        # Extract the specified channel
        max_channel = 2 if img.mode == 'RGB' else 3
        if channel > max_channel:
            channel = 0  # Default to red if invalid channel
        
        # Get the specified bit plane
        if bit_plane < 0 or bit_plane > 7:
            bit_plane = 0  # Default to LSB if invalid
        
        # Extract bits from the image
        extracted_bits = []
        for row in pixels:
            for pixel in row:
                # Get the bit at specified position
                if channel < len(pixel):
                    bit = (pixel[channel] >> bit_plane) & 1
                    extracted_bits.append(bit)
        
        # Convert bits to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits) // 8):
            byte = 0
            for j in range(8):
                if i*8 + j < len(extracted_bits):
                    byte = (byte << 1) | extracted_bits[i*8 + j]
            extracted_bytes.append(byte)
        
        # Check if the data looks like valid content
        confidence = assess_data_validity(extracted_bytes)
        
        # Create DecoderResult
        return DecoderResult(
            method=f"LSB (Channel: {channel}, Bit: {bit_plane})",
            data=bytes(extracted_bytes),
            success=confidence > 0.3,
            confidence=confidence,
            info={
                "bit_plane": bit_plane,
                "channel": channel,
                "total_bits": len(extracted_bits)
            }
        )
        
    except Exception as e:
        return DecoderResult(
            method=f"LSB (Channel: {channel}, Bit: {bit_plane})",
            success=False,
            confidence=0.0,
            info={"error": str(e)}
        )

def decode_multi_bit_lsb(image_path, bits=2, channel=0):
    """
    Extract data using multi-bit LSB steganography.
    
    Args:
        image_path: Path to the image file
        bits: Number of least significant bits to use (1-4)
        channel: Which color channel to use (0=R, 1=G, 2=B)
    
    Returns:
        DecoderResult object
    """
    try:
        # Limit bits to reasonable range
        if bits < 1 or bits > 4:
            bits = 2
        
        # Open the image
        img = Image.open(image_path)
        if img.mode != 'RGB' and img.mode != 'RGBA':
            img = img.convert('RGB')
        
        # Convert to numpy array
        pixels = np.array(img)
        
        # Extract data
        extracted_bits = []
        for row in pixels:
            for pixel in row:
                if channel < len(pixel):
                    # Extract the specified number of bits
                    for bit in range(bits):
                        extracted_bits.append((pixel[channel] >> bit) & 1)
        
        # Convert bits to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits) // 8):
            byte = 0
            for j in range(8):
                if i*8 + j < len(extracted_bits):
                    byte = (byte << 1) | extracted_bits[i*8 + j]
            extracted_bytes.append(byte)
        
        # Assess confidence
        confidence = assess_data_validity(extracted_bytes)
        
        return DecoderResult(
            method=f"Multi-bit LSB (Bits: {bits}, Channel: {channel})",
            data=bytes(extracted_bytes),
            success=confidence > 0.3,
            confidence=confidence,
            info={
                "bits_used": bits,
                "channel": channel
            }
        )
        
    except Exception as e:
        return DecoderResult(
            method=f"Multi-bit LSB (Bits: {bits}, Channel: {channel})",
            success=False,
            confidence=0.0,
            info={"error": str(e)}
        )

# Metadata Decoders
def extract_metadata_hidden_data(image_path):
    """
    Extract data hidden in metadata fields.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        DecoderResult object
    """
    try:
        # Run exiftool to extract metadata
        cmd = ["exiftool", "-j", image_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return DecoderResult(
                method="Metadata Extraction",
                success=False,
                confidence=0.0,
                info={"error": result.stderr}
            )
        
        # Parse the JSON result
        metadata = json.loads(result.stdout)
        if not metadata or not isinstance(metadata, list) or len(metadata) == 0:
            return DecoderResult(
                method="Metadata Extraction",
                success=False,
                confidence=0.1,
                info={"error": "No metadata found"}
            )
        
        metadata = metadata[0]  # exiftool returns a list with one item
        
        # Look for suspicious fields that might contain hidden data
        suspicious_fields = [
            "Comment", "UserComment", "Artist", "Copyright",
            "ImageDescription", "XPComment", "XPAuthor"
        ]
        
        extracted_data = []
        found_fields = {}
        
        for field in suspicious_fields:
            if field in metadata and metadata[field]:
                found_fields[field] = metadata[field]
                try:
                    # Try to decode as base64
                    decoded = base64.b64decode(metadata[field])
                    extracted_data.append(decoded)
                except:
                    # If not base64, store as is
                    extracted_data.append(metadata[field].encode('utf-8', errors='ignore'))
        
        # If no suspicious fields found, check all metadata for binary-looking data
        if not found_fields:
            for field, value in metadata.items():
                if isinstance(value, str) and len(value) > 20:
                    # Check if it might be binary data encoded as text
                    binary_likelihood = 0
                    for char in value:
                        if ord(char) < 32 or ord(char) > 126:
                            binary_likelihood += 1
                    
                    if binary_likelihood / len(value) > 0.1:
                        found_fields[field] = value
                        extracted_data.append(value.encode('utf-8', errors='ignore'))
        
        if not extracted_data:
            return DecoderResult(
                method="Metadata Extraction",
                success=False,
                confidence=0.2,
                info={"examined_fields": suspicious_fields}
            )
        
        # Combine all extracted data
        combined_data = b''.join(extracted_data)
        confidence = assess_data_validity(combined_data)
        
        return DecoderResult(
            method="Metadata Extraction",
            data=combined_data,
            success=confidence > 0.3,
            confidence=confidence,
            info={
                "found_fields": found_fields,
                "field_count": len(found_fields)
            }
        )
        
    except Exception as e:
        return DecoderResult(
            method="Metadata Extraction",
            success=False,
            confidence=0.0,
            info={"error": str(e)}
        )

# External tool wrappers
def try_steghide_extract(image_path, passphrase=""):
    """
    Attempt to extract data using steghide.
    
    Args:
        image_path: Path to the image file
        passphrase: Optional passphrase to try
    
    Returns:
        DecoderResult object
    """
    try:
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Run steghide to attempt extraction
        cmd = ["steghide", "extract", "-sf", image_path, "-p", passphrase, "-xf", output_path, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            if os.path.exists(output_path):
                os.unlink(output_path)
            return DecoderResult(
                method="Steghide",
                success=False,
                confidence=0.0,
                info={"error": result.stderr, "passphrase_used": bool(passphrase)}
            )
        
        # Read the extracted data
        with open(output_path, "rb") as f:
            extracted_data = f.read()
        
        # Clean up the temporary file
        os.unlink(output_path)
        
        # Assess the data
        confidence = assess_data_validity(extracted_data)
        
        return DecoderResult(
            method="Steghide",
            data=extracted_data,
            success=True,
            confidence=max(0.8, confidence),  # High confidence if steghide succeeded
            info={
                "passphrase_used": bool(passphrase),
                "passphrase": passphrase if passphrase else None
            }
        )
        
    except Exception as e:
        if "output_path" in locals() and os.path.exists(output_path):
            os.unlink(output_path)
        return DecoderResult(
            method="Steghide",
            success=False,
            confidence=0.0,
            info={"error": str(e)}
        )

def try_outguess_extract(image_path, passphrase=""):
    """
    Attempt to extract data using outguess.
    
    Args:
        image_path: Path to the image file
        passphrase: Optional passphrase to try
    
    Returns:
        DecoderResult object
    """
    try:
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Run outguess to attempt extraction
        cmd = ["outguess", "-r", "-k", passphrase, image_path, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            if os.path.exists(output_path):
                os.unlink(output_path)
            return DecoderResult(
                method="Outguess",
                success=False,
                confidence=0.0,
                info={"error": result.stderr, "passphrase_used": bool(passphrase)}
            )
        
        # Read the extracted data
        with open(output_path, "rb") as f:
            extracted_data = f.read()
        
        # Clean up the temporary file
        os.unlink(output_path)
        
        # Assess the data
        confidence = assess_data_validity(extracted_data)
        
        return DecoderResult(
            method="Outguess",
            data=extracted_data,
            success=True,
            confidence=max(0.8, confidence),  # High confidence if outguess succeeded
            info={
                "passphrase_used": bool(passphrase),
                "passphrase": passphrase if passphrase else None
            }
        )
        
    except Exception as e:
        if "output_path" in locals() and os.path.exists(output_path):
            os.unlink(output_path)
        return DecoderResult(
            method="Outguess",
            success=False,
            confidence=0.0,
            info={"error": str(e)}
        )

# Utility functions
def assess_data_validity(data):
    """
    Assess how likely it is that the data contains meaningful content.
    
    Args:
        data: Bytes object to analyze
    
    Returns:
        Confidence score from 0.0 to 1.0
    """
    if not data or len(data) < 4:
        return 0.0
    
    confidence = 0.0
    
    # Check for common file signatures
    file_signatures = {
        b'\x89PNG': 0.9,  # PNG
        b'BM': 0.9,       # BMP
        b'\xFF\xD8\xFF': 0.9,  # JPEG
        b'GIF8': 0.9,     # GIF
        b'PK': 0.8,       # ZIP/DOCX/etc
        b'%PDF': 0.9,     # PDF
        b'\x7FELF': 0.8,  # ELF binary
        b'MZ': 0.8,       # Windows executable
    }
    
    for sig, conf in file_signatures.items():
        if data.startswith(sig):
            return conf
    
    # Check for plaintext
    try:
        text = data.decode('utf-8', errors='ignore')
        printable_ratio = sum(c.isprintable() for c in text) / len(text)
        
        if printable_ratio > 0.9:
            # Likely text
            if any(marker in text.lower() for marker in ['http://', 'https://', '.com', '.org', '.net']):
                confidence = max(confidence, 0.8)  # Contains URLs
            
            if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
                confidence = max(confidence, 0.8)  # Contains emails
            
            word_pattern = r'\b[A-Za-z]{3,15}\b'
            words = re.findall(word_pattern, text)
            
            if len(words) > 5:
                # Probably contains actual text
                confidence = max(confidence, 0.7)
                
                # Check for meaningful word transitions
                meaningful_transitions = 0
                for i in range(len(words) - 1):
                    if len(words[i]) > 2 and len(words[i+1]) > 2:
                        meaningful_transitions += 1
                
                if meaningful_transitions > 3:
                    confidence = max(confidence, 0.85)
    except:
        pass
    
    # Check for base64
    try:
        base64.b64decode(data)
        # If successful and data looks like base64
        if re.match(r'^[A-Za-z0-9+/=]+$', data.decode('ascii', errors='ignore')):
            confidence = max(confidence, 0.6)
    except:
        pass
    
    # Check entropy
    entropy = calculate_entropy(data)
    if 4.0 < entropy < 5.5:
        # Likely compressed/encrypted data
        confidence = max(confidence, 0.5)
    
    return confidence

def calculate_entropy(data):
    """Calculate Shannon entropy of data."""
    if not data:
        return 0.0
    
    entropy = 0
    for x in range(256):
        p_x = data.count(x)/len(data)
        if p_x > 0:
            entropy += -p_x * np.log2(p_x)
    return entropy

# Brute Force Decoders
def brute_force_decode(image_path, password_list=None):
    """
    Attempt to decode steganographic content using multiple methods.
    
    Args:
        image_path: Path to the image file
        password_list: Optional list of passwords to try
    
    Returns:
        List of DecoderResult objects
    """
    results = []
    
    # Set default password list if none provided
    if not password_list:
        password_list = ["", "password", "123456", "admin", "stego", "secret", "hidden"]
    
    # Try LSB decoding with different parameters
    for channel in range(3):  # R, G, B channels
        for bit_plane in [0, 1]:  # Focus on lower bit planes
            results.append(decode_lsb(image_path, bit_plane, channel))
    
    # Try multi-bit LSB
    for channel in range(3):
        results.append(decode_multi_bit_lsb(image_path, bits=2, channel=channel))
    
    # Try metadata extraction
    results.append(extract_metadata_hidden_data(image_path))
    
    # Try external tools with different passwords
    for password in password_list:
        try:
            # Steghide
            steghide_result = try_steghide_extract(image_path, password)
            if steghide_result.success:
                results.append(steghide_result)
                # If successful, no need to try more passwords
                break
            
            # Only add failed result if it's the empty password
            if password == "":
                results.append(steghide_result)
        except:
            pass
    
    for password in password_list:
        try:
            # Outguess
            outguess_result = try_outguess_extract(image_path, password)
            if outguess_result.success:
                results.append(outguess_result)
                # If successful, no need to try more passwords
                break
            
            # Only add failed result if it's the empty password
            if password == "":
                results.append(outguess_result)
        except:
            pass
    
    # Sort by confidence
    results.sort(key=lambda x: x.confidence, reverse=True)
    
    return results