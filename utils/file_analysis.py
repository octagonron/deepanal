import subprocess
import os
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd

def run_command(cmd, input_file):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd + [input_file],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running {cmd[0]}: {e.stderr}"

def get_file_metadata(file_path):
    """Extract file metadata using exiftool."""
    output = run_command(['exiftool'], file_path)
    metadata = {}
    for line in output.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    return metadata

def extract_strings(file_path, min_length=4):
    """Extract readable strings from the file."""
    output = run_command(['strings', '-n', str(min_length)], file_path)
    return output.split('\n')

def analyze_file_structure(file_path):
    """Analyze file structure using binwalk."""
    output = run_command(['binwalk'], file_path)
    return output

def calculate_entropy(file_path):
    """Calculate byte-level entropy of the file."""
    with open(file_path, 'rb') as f:
        data = f.read()
    
    if len(data) == 0:
        return 0
    
    entropy = 0
    for x in range(256):
        p_x = data.count(x)/len(data)
        if p_x > 0:
            entropy += -p_x * np.log2(p_x)
    return entropy

def get_byte_frequency(file_path):
    """Get byte frequency distribution."""
    with open(file_path, 'rb') as f:
        data = f.read()
    
    freq = pd.Series(list(data)).value_counts()
    return freq.index.tolist(), freq.values.tolist()

def get_hex_dump(file_path, num_bytes=256):
    """Get hexadecimal dump of the file."""
    output = run_command(['xxd', '-l', str(num_bytes)], file_path)
    return output
