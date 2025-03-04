import streamlit as st
import tempfile
import os
from pathlib import Path
from utils.file_analysis import (
    get_file_metadata, extract_strings, analyze_file_structure,
    calculate_entropy, get_byte_frequency, get_hex_dump
)
from utils.visualizations import (
    create_entropy_plot, create_byte_frequency_plot, format_hex_dump
)

st.set_page_config(
    page_title="DEEP ANAL: Steganography Analysis",
    page_icon="🔍",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Display banner
with open('assets/banner.svg') as f:
    st.markdown(f'<div style="text-align: center">{f.read()}</div>', unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center'>
        <p>Upload an image file (PNG/JPEG) for steganography analysis</p>
    </div>
""", unsafe_allow_html=True)

# File upload
uploaded_file = st.file_uploader(
    "Drop your file here",
    type=['png', 'jpg', 'jpeg'],
    help="Supported formats: PNG, JPEG"
)

if uploaded_file:
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name

    try:
        # Create two columns for the layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("File Analysis")
            
            # Metadata
            with st.expander("📋 File Metadata", expanded=True):
                metadata = get_file_metadata(temp_path)
                for key, value in metadata.items():
                    st.text(f"{key}: {value}")

            # String Analysis
            with st.expander("🔤 String Analysis", expanded=True):
                strings = extract_strings(temp_path)
                st.code("\n".join(strings[:100]))

            # File Structure
            with st.expander("📁 File Structure", expanded=True):
                structure = analyze_file_structure(temp_path)
                st.code(structure)

        with col2:
            st.subheader("Visualizations")

            # Entropy Analysis
            entropy = calculate_entropy(temp_path)
            st.plotly_chart(
                create_entropy_plot(entropy),
                use_container_width=True
            )

            # Byte Frequency
            bytes_values, frequencies = get_byte_frequency(temp_path)
            st.plotly_chart(
                create_byte_frequency_plot(bytes_values, frequencies),
                use_container_width=True
            )

            # Hex Dump
            with st.expander("📝 Hex Dump", expanded=True):
                hex_dump = get_hex_dump(temp_path)
                st.markdown(format_hex_dump(hex_dump), unsafe_allow_html=True)

    finally:
        # Cleanup temporary file
        os.unlink(temp_path)
else:
    st.info("👆 Upload a file to begin analysis")

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 10px;'>
        <p>🔍 DEEP ANAL: Advanced Steganography Analysis Tool</p>
        <p style='font-size: 0.8rem; color: #666;'>Analyze deeper. Find hidden data.</p>
    </div>
""", unsafe_allow_html=True)
