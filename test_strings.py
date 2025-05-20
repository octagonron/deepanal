import streamlit as st
import numpy as np
import random

# Simple test to check if string visualization works
st.title("DEEP ANAL - String Visualization Test")

# Create some test strings
test_strings = [
    "steganography", "analysis", "cyberpunk", "visualization", 
    "hidden", "data", "entropy", "frequency", "extraction",
    "patterns", "detection", "algorithm", "pixels", "bytes",
    "information", "security", "forensics", "cryptography",
    "encoding", "deep", "neural", "networks", "machine", "learning"
]

# Duplicate some strings to create varying frequencies
duplicated_strings = test_strings.copy()
for _ in range(5):
    duplicated_strings.extend(random.sample(test_strings, 10))

# Just import and try to display basic text
st.write("Basic test - if you see this, Streamlit is working")

# Try to import visualization module but don't use it yet
st.write("Attempting to import visualization module...")
try:
    from utils.visualizations import create_strings_visualization
    st.success("Successfully imported visualization module")
    
    # Try creating a simple strings visualization
    st.write("Creating string visualization...")
    strings_viz = create_strings_visualization(duplicated_strings[:50])
    st.plotly_chart(strings_viz, use_container_width=True)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("Stack trace:")
    import traceback
    st.code(traceback.format_exc())