import streamlit as st
import tempfile
import os
import json
import datetime
from pathlib import Path
from utils.file_analysis import (
    get_file_metadata, extract_strings, analyze_file_structure,
    calculate_entropy, get_byte_frequency, get_hex_dump, run_zsteg
)
from utils.visualizations import (
    create_entropy_plot, create_byte_frequency_plot, format_hex_dump,
    create_detailed_view
)
from utils.database import (
    save_analysis, get_recent_analyses, get_analysis_by_id, DB_AVAILABLE
)
from utils.stego_detector import analyze_image_for_steganography

# Configure Streamlit page
st.set_page_config(
    page_title="DEEP ANAL: Steganography Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
custom_css = """
<style>
/* Main DEEP ANAL Styling */
.info-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: rgba(0, 255, 255, 0.2);
    color: #00ffff;
    font-weight: bold;
    cursor: pointer;
    margin-left: 8px;
    font-size: 14px;
}

.info-tooltip {
    position: relative;
    display: inline-block;
}

.info-tooltip .info-tooltip-text {
    visibility: hidden;
    width: 300px;
    background-color: rgba(0, 10, 30, 0.9);
    color: #00ffff;
    text-align: left;
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    z-index: 1000;
    top: 125%;
    left: 50%;
    margin-left: -150px;
    opacity: 0;
    transition: opacity 0.3s;
    border: 1px solid #ff00ff;
    font-family: monospace;
    font-size: 0.9em;
}

.info-tooltip:hover .info-tooltip-text {
    visibility: visible;
    opacity: 1;
}

/* Custom container for cyberpunk visualizations */
.visualization-container {
    border: 1px solid #ff00ff;
    border-radius: 10px;
    padding: 10px;
    background-color: rgba(10, 10, 30, 0.5);
    margin-bottom: 20px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Create info button with tooltip
def info_button(id_name, info_text):
    return f"""
    <div class="info-tooltip" id="{id_name}">
        <span class="info-button">i</span>
        <div class="info-tooltip-text">{info_text}</div>
    </div>
    """

# Display banner
st.markdown("""
<div style="text-align: center; background-color: rgba(0, 10, 30, 0.7); padding: 20px; 
            border-radius: 10px; border: 1px solid #00ffff; margin-bottom: 20px;">
    <h1 style="color: #ff00ff; font-family: monospace; text-shadow: 0 0 10px rgba(255, 0, 255, 0.5);">
        DEEP ANAL
    </h1>
    <h3 style="color: #00ffff; font-family: monospace;">
        Hardcore Steganography Analysis
    </h3>
</div>
""", unsafe_allow_html=True)

# Main content - File upload
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
        # Run initial analysis
        file_size = os.path.getsize(temp_path)
        file_type = Path(uploaded_file.name).suffix.lower()[1:]  # Remove the dot
        entropy_value = calculate_entropy(temp_path)
        metadata = get_file_metadata(temp_path)
        is_image = file_type in ['png', 'jpg', 'jpeg']
        
        # Only PNG and JPEG images are supported for advanced analysis
        if is_image:
            # Run stego detection
            detection_result = analyze_image_for_steganography(temp_path)
            likelihood = detection_result.likelihood
            likelihood_percentage = f"{likelihood*100:.1f}%"
            
            # Determine color based on likelihood
            color = "#00ff00" if likelihood < 0.4 else "#ffff00" if likelihood < 0.7 else "#ff0000"
            
            # Save analysis to database if available
            if DB_AVAILABLE:
                # Convert metadata to JSON string
                metadata_json = json.dumps(metadata)
                # Save to database (no thumbnail for now)
                save_analysis(
                    uploaded_file.name, file_size, file_type, 
                    entropy_value, metadata_json
                )
        
            # Display analysis results
            st.markdown(f"""
            <div style="border: 2px solid {color}; padding: 15px; border-radius: 10px; 
                        background-color: rgba(0,0,20,0.8); margin-bottom: 20px;">
                <h2 style="color: #ff00ff; font-family: monospace;">
                    Analysis Results: {uploaded_file.name}
                </h2>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <span style="color: #00ffff; font-family: monospace;">
                        Size: {file_size} bytes
                    </span>
                    <span style="color: #ff00ff; font-family: monospace;">
                        Type: {file_type.upper()}
                    </span>
                    <span style="color: #ffff00; font-family: monospace;">
                        Entropy: {entropy_value:.4f}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display a prominent banner showing the likelihood
            st.markdown(f"""
            <div style="margin-bottom: 25px; padding: 15px; border-radius: 10px; 
                        background: linear-gradient(90deg, rgba(0,0,20,0.9) 0%, rgba(20,0,40,0.9) 100%);
                        border: 2px solid {color}; text-align: center;">
                <h2 style="color: {color}; font-family: monospace; margin-bottom: 5px;">
                    Steganography Detection: {likelihood_percentage}
                </h2>
                <p style="color: #ffffff; font-family: monospace; font-size: 1.1em;">
                    {detection_result.main_finding}
                </p>
                <div style="margin-top: 10px; font-size: 0.9em; color: #00ffff; font-family: monospace;">
                    <span style="color: #ffff00;">Potential Techniques:</span> 
                    {", ".join(detection_result.techniques) if hasattr(detection_result, "techniques") and detection_result.techniques else "None identified"}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create columns for structured layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Entropy visualization with info button
                entropy_info = "Entropy measures the randomness of data. Higher values (closer to 8) indicate more randomness and potential hidden information."
                st.markdown(f"### Entropy Visualization {info_button('entropy-info', entropy_info)}", unsafe_allow_html=True)
                
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                entropy_plot = create_entropy_plot(entropy_value)
                st.plotly_chart(entropy_plot, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Byte frequency visualization with info button
                byte_info = "Byte frequency distribution shows how often each byte value (0-255) appears in the file. Unusual patterns may indicate hidden data."
                st.markdown(f"### Byte Frequency Analysis {info_button('byte-info', byte_info)}", unsafe_allow_html=True)
                
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                bytes_values, frequencies = get_byte_frequency(temp_path)
                st.plotly_chart(
                    create_byte_frequency_plot(bytes_values, frequencies),
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # File metadata with info button
                metadata_info = "Metadata includes information embedded in file headers that might contain clues about hidden data or file manipulation."
                st.markdown(f"### File Metadata {info_button('metadata-info', metadata_info)}", unsafe_allow_html=True)
                
                for key, value in metadata.items():
                    st.markdown(f"**{key}:** {value}")
            
            with col2:
                # Steganography Detection Details with info button
                stego_info = "Detection indicators measure various statistical properties that can reveal hidden data. Higher values suggest higher likelihood of steganography."
                st.markdown(f"### Steganography Detection Details {info_button('stego-info', stego_info)}", unsafe_allow_html=True)
                
                # Create table with all the detection indicators
                st.markdown("#### Detection Indicators")
                
                # Create a table header
                st.markdown("""
                <div style="display: grid; grid-template-columns: 3fr 1fr 1fr; gap: 10px; margin-bottom: 10px; 
                            background: rgba(0,0,0,0.2); padding: 8px; border-radius: 5px;">
                    <div style="color: #00ffff; font-family: monospace; font-weight: bold;">Indicator</div>
                    <div style="color: #00ffff; font-family: monospace; font-weight: bold;">Value</div>
                    <div style="color: #00ffff; font-family: monospace; font-weight: bold;">Weight</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display each indicator
                for name, details in detection_result.indicators.items():
                    value = details["value"]
                    weight = details["weight"]
                    
                    # Determine color based on value
                    value_color = "#00ff00" if value < 0.4 else "#ffff00" if value < 0.7 else "#ff0000"
                    
                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: 3fr 1fr 1fr; gap: 10px; margin-bottom: 5px; 
                                background: rgba(0,0,0,0.1); padding: 8px; border-radius: 5px;">
                        <div style="color: #ffffff; font-family: monospace;">
                            {name.replace('_', ' ').title()}
                        </div>
                        <div style="color: {value_color}; font-family: monospace; font-weight: bold;">
                            {value:.3f}
                        </div>
                        <div style="color: #00ffff; font-family: monospace;">
                            {weight:.1f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display explanation
                st.markdown("#### Analysis Explanation")
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; background: rgba(0,10,20,0.5); margin-bottom: 15px;">
                    <p style="color: #ffffff; font-family: monospace;">
                        {detection_result.explanation}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # ZSTEG Output (for PNG files)
                if file_type.lower() == 'png':
                    zsteg_info = "ZSTEG is a tool specifically designed to detect various steganography techniques in PNG files, scanning multiple bit planes and channels."
                    st.markdown(f"### ZSTEG Analysis {info_button('zsteg-info', zsteg_info)}", unsafe_allow_html=True)
                    
                    # Run ZSTEG with -a option
                    zsteg_output = run_zsteg(temp_path)
                    
                    # Display the output in a scrollable area with syntax highlighting
                    st.markdown("""
                    <div style="max-height: 300px; overflow-y: auto; background: rgba(0,0,20,0.8); 
                                border: 1px solid #00ffff; border-radius: 5px; padding: 10px; 
                                font-family: monospace; color: #00ffff; margin-bottom: 15px;">
                    """, unsafe_allow_html=True)
                    
                    # Format the output with colors
                    formatted_output = zsteg_output.replace('\n', '<br>')
                    # Highlight specific patterns in the output
                    formatted_output = formatted_output.replace('[+]', '<span style="color: #00ff00; font-weight: bold;">[+]</span>')
                    formatted_output = formatted_output.replace('[!]', '<span style="color: #ff0000; font-weight: bold;">[!]</span>')
                    formatted_output = formatted_output.replace('=>', '<span style="color: #ffff00;">=></span>')
                    
                    st.markdown(f"{formatted_output}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional analysis sections (full width)
            # String Analysis with info button
            strings_info = "String extraction identifies ASCII text within binary data that could represent hidden messages or embedded content."
            st.markdown(f"### String Analysis {info_button('strings-info', strings_info)}", unsafe_allow_html=True)
            
            strings = extract_strings(temp_path)
            st.code("\n".join(strings[:100]))

            # File Structure with info button
            structure_info = "File structure analysis examines the binary structure of the file to find embedded files, abnormal patterns, or hidden data streams."
            st.markdown(f"### File Structure {info_button('structure-info', structure_info)}", unsafe_allow_html=True)
            
            structure = analyze_file_structure(temp_path)
            st.code(structure)
            
            # Hex Dump with info button
            hex_info = "Hexadecimal dump displays the raw binary data of the file, which can reveal hidden patterns or anomalies not visible in other analyses."
            st.markdown(f"### Hex Dump {info_button('hex-info', hex_info)}", unsafe_allow_html=True)
            
            hex_dump = get_hex_dump(temp_path)
            st.markdown(format_hex_dump(hex_dump), unsafe_allow_html=True)
            
            # Mobile App Version Info
            st.markdown("### 📱 Mobile App Version")
            st.markdown("""
            <div style="display: flex; justify-content: space-between; margin: 20px 0;">
                <div style="text-align: center; padding: 10px; background: rgba(0,0,30,0.5); 
                            border-radius: 10px; width: 48%; border: 1px solid #00ffff;">
                    <h4 style="color: #00ffff; font-family: monospace;">iOS Version</h4>
                    <p style="color: #ffffff; font-family: monospace;">
                        Available on the App Store
                    </p>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(0,0,30,0.5); 
                            border-radius: 10px; width: 48%; border: 1px solid #00ffff;">
                    <h4 style="color: #00ffff; font-family: monospace;">Android Version</h4>
                    <p style="color: #ffffff; font-family: monospace;">
                        Available on Google Play
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display basic analysis for non-image files
            st.markdown(f"""
            <div style="border: 2px solid #00ffff; padding: 15px; border-radius: 10px; 
                        background-color: rgba(0,0,20,0.8); margin-bottom: 20px;">
                <h2 style="color: #ff00ff; font-family: monospace;">
                    Basic Analysis Results: {uploaded_file.name}
                </h2>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <span style="color: #00ffff; font-family: monospace;">
                        Size: {file_size} bytes
                    </span>
                    <span style="color: #ff00ff; font-family: monospace;">
                        Type: {file_type.upper()}
                    </span>
                    <span style="color: #ffff00; font-family: monospace;">
                        Entropy: {entropy_value:.4f}
                    </span>
                </div>
                <p style="color: #ffffff; font-family: monospace; margin-top: 15px;">
                    Advanced steganography analysis is only available for PNG and JPEG images.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Basic analysis tabs
            st.markdown("### Basic File Analysis")
            # Create columns for layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Entropy visualization with info button
                entropy_info = "Entropy measures the randomness of data. Higher values (closer to 8) indicate more randomness and potential hidden information."
                st.markdown(f"### Entropy Analysis {info_button('entropy-info', entropy_info)}", unsafe_allow_html=True)
                
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                entropy_plot = create_entropy_plot(entropy_value)
                st.plotly_chart(entropy_plot, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # String Analysis with info button
                strings_info = "String extraction identifies ASCII text within binary data that could represent hidden messages or embedded content."
                st.markdown(f"### String Analysis {info_button('strings-info', strings_info)}", unsafe_allow_html=True)
                
                strings = extract_strings(temp_path)
                st.code("\n".join(strings[:100]))
            
            with col2:
                # File metadata with info button
                metadata_info = "Metadata includes information embedded in file headers that might contain clues about hidden data or file manipulation."
                st.markdown(f"### File Metadata {info_button('metadata-info', metadata_info)}", unsafe_allow_html=True)
                
                for key, value in metadata.items():
                    st.markdown(f"**{key}:** {value}")
                
                # File Structure with info button
                structure_info = "File structure analysis examines the binary structure of the file to find embedded files, abnormal patterns, or hidden data streams."
                st.markdown(f"### File Structure {info_button('structure-info', structure_info)}", unsafe_allow_html=True)
                
                structure = analyze_file_structure(temp_path)
                st.code(structure)
            
            # Hex Dump (full width) with info button
            hex_info = "Hexadecimal dump displays the raw binary data of the file, which can reveal hidden patterns or anomalies not visible in other analyses."
            st.markdown(f"### Hex Dump {info_button('hex-info', hex_info)}", unsafe_allow_html=True)
            
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