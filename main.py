import streamlit as st
import tempfile
import os
from pathlib import Path
from utils.file_analysis import (
    get_file_metadata, extract_strings, analyze_file_structure,
    calculate_entropy, get_byte_frequency, get_hex_dump
)
from utils.visualizations import (
    create_entropy_plot, create_byte_frequency_plot, format_hex_dump,
    create_detailed_view
)

st.set_page_config(
    page_title="DEEP ANAL: Steganography Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Display banner
with open('assets/banner.svg') as f:
    st.markdown(f'<div style="text-align: center">{f.read()}</div>', unsafe_allow_html=True)

# Initialize session state for detailed view
if 'show_detailed_view' not in st.session_state:
    st.session_state.show_detailed_view = None

# File upload
uploaded_file = st.file_uploader(
    "Drop your file here",
    type=['png', 'jpg', 'jpeg'],
    help="Supported formats: PNG, JPEG",
    key="file_uploader"
)

if uploaded_file:
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name

    try:
        # Check if detailed view is requested
        if st.session_state.show_detailed_view:
            st.markdown("""
                <div class="fullscreen-view">
                    <div class="fullscreen-content">
            """, unsafe_allow_html=True)

            if st.button("Close", key="close_detailed", class_name="close-button"):
                st.session_state.show_detailed_view = None
                st.experimental_rerun()

            # Show detailed content based on selected analysis
            analysis_type = st.session_state.show_detailed_view
            if analysis_type == "entropy":
                entropy = calculate_entropy(temp_path)
                st.plotly_chart(
                    create_detailed_view(
                        create_entropy_plot(entropy),
                        "Detailed Entropy Analysis"
                    ),
                    use_container_width=True
                )
            elif analysis_type == "frequency":
                bytes_values, frequencies = get_byte_frequency(temp_path)
                st.plotly_chart(
                    create_detailed_view(
                        create_byte_frequency_plot(bytes_values, frequencies),
                        "Detailed Byte Frequency Analysis"
                    ),
                    use_container_width=True
                )

            st.markdown("</div></div>", unsafe_allow_html=True)

        else:
            # Create two columns for the layout
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("File Analysis")

                # Metadata
                with st.expander("📋 File Metadata", expanded=True):
                    metadata = get_file_metadata(temp_path)
                    for key, value in metadata.items():
                        st.markdown(f"**{key}:** {value}")

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
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                st.plotly_chart(
                    create_entropy_plot(entropy),
                    use_container_width=True
                )
                if st.button("View Detailed Entropy Analysis", key="entropy_detail"):
                    st.session_state.show_detailed_view = "entropy"
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

                # Byte Frequency
                bytes_values, frequencies = get_byte_frequency(temp_path)
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                st.plotly_chart(
                    create_byte_frequency_plot(bytes_values, frequencies),
                    use_container_width=True
                )
                if st.button("View Detailed Frequency Analysis", key="frequency_detail"):
                    st.session_state.show_detailed_view = "frequency"
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

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
    <div style='text-align: center; margin-top: 2rem; padding: 1rem; background: rgba(26,26,46,0.6); border-radius: 10px; border: 1px solid rgba(255,75,75,0.3);'>
        <p style='color: #ff4b4b; font-size: 1.2rem;'>🔍 DEEP ANAL: Advanced Steganography Analysis Tool</p>
        <p style='color: #7b2bf9; font-size: 0.9rem;'>Analyze deeper. Find hidden data.</p>
    </div>
""", unsafe_allow_html=True)