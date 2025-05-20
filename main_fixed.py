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

# Enable more immersive UI experience
st.markdown("""
<style>
    /* Full cyberpunk theme overrides */
    .stApp {
        background-color: #000010;
        background-image: 
            radial-gradient(circle at 20% 90%, rgba(28, 0, 50, 0.4) 0%, transparent 20%),
            radial-gradient(circle at 80% 10%, rgba(0, 50, 90, 0.4) 0%, transparent 20%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0, 20, 40, 0.3);
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 0, 60, 0.3);
        border-radius: 5px;
        color: #00ffff;
        border: 1px solid rgba(0, 255, 255, 0.2);
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(80, 0, 160, 0.5);
        border: 1px solid rgba(255, 0, 255, 0.4);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(120, 0, 170, 0.6) !important;
        border: 1px solid #ff00ff !important;
    }
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00ffff;
        font-family: monospace;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    h1 {
        color: #ff00ff;
        text-shadow: 0 0 10px rgba(255, 0, 255, 0.5);
    }
    /* Code blocks */
    .stCodeBlock {
        background-color: rgba(0, 20, 30, 0.6) !important;
        border: 1px solid rgba(0, 255, 255, 0.2) !important;
        border-radius: 10px !important;
    }
    /* Button styling */
    .stButton button {
        background-color: rgba(80, 0, 160, 0.6);
        color: #00ffff;
        border: 1px solid rgba(0, 255, 255, 0.4);
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: rgba(120, 0, 170, 0.8);
        border: 1px solid #ff00ff;
        color: #ffffff;
    }
    /* File uploader */
    .stFileUploader {
        background-color: rgba(0, 20, 40, 0.3);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 255, 0.2);
    }
    /* Dataframes */
    .stDataFrame {
        background-color: rgba(0, 15, 30, 0.5);
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 255, 0.2);
        overflow: hidden;
    }
    /* Expander */
    .stExpander {
        background-color: rgba(20, 0, 40, 0.4);
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 255, 0.2);
    }
    /* Text input, number input, etc. */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: rgba(0, 20, 30, 0.6);
        color: #00ffff;
        border: 1px solid rgba(0, 255, 255, 0.4);
        border-radius: 5px;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border: 1px solid #ff00ff;
        box-shadow: 0 0 5px rgba(255, 0, 255, 0.5);
    }
    /* Metrics/KPIs */
    .stMetric {
        background-color: rgba(0, 20, 30, 0.4);
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 10px;
    }
    .stMetric label {
        color: #00ffff;
    }
    .stMetric .css-1wivap2 {
        color: #ff00ff;
    }
    /* Grid size and layout adjustments */
    [data-testid="stVerticalBlock"] > div {
        gap: 15px;
    }
</style>
""", unsafe_allow_html=True)

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

# Display banner with logo reference
from pathlib import Path

# Check if the custom logo exists
logo_path = Path("attached_assets/DEEPANAL.png")
if logo_path.exists():
    # Use the custom logo if available
    st.markdown("""
    <div style="text-align: center; background-color: rgba(0, 10, 30, 0.7); padding: 20px; 
                border-radius: 10px; border: 1px solid #00ffff; margin-bottom: 20px; 
                display: flex; flex-direction: column; align-items: center;">
        <div style="max-width: 600px; margin-bottom: 10px;">
            <img src="attached_assets/DEEPANAL.png" style="width: 100%; height: auto;">
        </div>
        <h3 style="color: #00ffff; font-family: monospace; margin-top: 5px;">
            Steganography Analysis
        </h3>
    </div>
    """, unsafe_allow_html=True)
else:
    # Fallback to text-only banner if image is not available
    st.markdown("""
    <div style="text-align: center; background-color: rgba(0, 10, 30, 0.7); padding: 20px; 
                border-radius: 10px; border: 1px solid #00ffff; margin-bottom: 20px;">
        <h1 style="color: #ff00ff; font-family: monospace; text-shadow: 0 0 10px rgba(255, 0, 255, 0.5);">
            DEEP ANAL
        </h1>
        <h3 style="color: #00ffff; font-family: monospace;">
            Steganography Analysis
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
# Add holographic effect to page
st.markdown("""
<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 999; 
            background: linear-gradient(45deg, rgba(255,0,255,0.05) 0%, rgba(0,255,255,0.05) 100%), 
                        repeating-linear-gradient(45deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 5px, rgba(0,255,255,0.03) 5px, rgba(255,0,255,0.03) 10px);">
</div>

<style>
    /* 3D Grid Effect for Background - Matches concept art */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px),
            linear-gradient(rgba(255,0,255,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,0,255,0.05) 1px, transparent 1px);
        background-size: 100px 100px, 100px 100px, 20px 20px, 20px 20px;
        background-position: -2px -2px, -2px -2px, -1px -1px, -1px -1px;
        transform: perspective(500px) rotateX(60deg);
        transform-origin: center bottom;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Panel styling to match concept art */
    .stTabs [data-baseweb="tab-panel"] {
        background: rgba(0,10,30,0.7);
        border: 1px solid #ff00ff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(255,0,255,0.3);
    }
    
    /* Make visualization containers more holographic */
    .visualization-container {
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 0 15px rgba(0,255,255,0.4),
            inset 0 0 10px rgba(255,0,255,0.3);
    }
    
    .visualization-container::before {
        content: "";
        position: absolute;
        top: -10%;
        left: -10%;
        width: 120%;
        height: 120%;
        background: linear-gradient(45deg, 
            rgba(255,0,255,0) 0%, 
            rgba(255,0,255,0.1) 25%, 
            rgba(0,255,255,0.1) 50%, 
            rgba(255,0,255,0.1) 75%, 
            rgba(255,0,255,0) 100%);
        pointer-events: none;
        animation: holographic-sweep 3s infinite linear;
        z-index: 10;
    }
    
    @keyframes holographic-sweep {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
</style>
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
            # Run stego detection with enhanced sensitivity algorithms
            try:
                detection_result = analyze_image_for_steganography(temp_path)
                likelihood = detection_result.likelihood
                likelihood_percentage = f"{likelihood*100:.1f}%"
                
                # Determine color based on likelihood
                color = "#00ff00" if likelihood < 0.3 else "#ffff00" if likelihood < 0.6 else "#ff0000"
                
                # Add debugging for hidden message detection
                st.session_state['last_analysis'] = {
                    'filename': uploaded_file.name,
                    'likelihood': likelihood,
                    'indicators': detection_result.indicators,
                    'techniques': detection_result.techniques if hasattr(detection_result, 'techniques') else []
                }
            except Exception as e:
                st.error(f"Error in steganography detection: {str(e)}")
                # Fallback values
                likelihood = 0
                likelihood_percentage = "0.0%"
                color = "#00ff00"
                detection_result = None
            
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
                    {detection_result.main_finding if detection_result else "Analysis error - no results available"}
                </p>
                <div style="margin-top: 10px; font-size: 0.9em; color: #00ffff; font-family: monospace;">
                    <span style="color: #ffff00;">Potential Techniques:</span> 
                    {", ".join(detection_result.techniques) if detection_result and hasattr(detection_result, "techniques") and detection_result.techniques else "None identified"}
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
                metadata_info = "Metadata includes information embedded in file headers that could contain clues about the file's origin or modifications."
                st.markdown(f"### File Metadata {info_button('metadata-info', metadata_info)}", unsafe_allow_html=True)
                
                if metadata:
                    with st.expander("View detailed metadata", expanded=False):
                        # Format metadata as a more readable table
                        st.markdown("""
                        <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                                    border: 1px solid #00ffff; font-family: monospace; color: #00ffff;">
                        """, unsafe_allow_html=True)
                        
                        for key, value in metadata.items():
                            st.markdown(f"""
                            <div style="display: flex; margin-bottom: 5px; border-bottom: 1px solid rgba(0,255,255,0.2); padding-bottom: 5px;">
                                <div style="flex: 1; color: #ff00ff;">{key}</div>
                                <div style="flex: 2; color: #ffffff;">{value}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No metadata found in the file.")
            
            with col2:
                # Strings extraction with info button
                strings_info = "Extracted readable text strings from the file that might reveal hidden messages or commands."
                st.markdown(f"### Extracted Strings {info_button('strings-info', strings_info)}", unsafe_allow_html=True)
                
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                strings = extract_strings(temp_path)
                
                # Display extracted strings with cyberpunk styling
                if strings:
                    # Display a word cloud visualization for the strings
                    st.markdown("#### Strings Word Cloud")
                    # We'll just show a message instead of the visualization since it's causing issues
                    st.markdown("""
                    <div style="text-align: center; padding: 20px; background-color: rgba(0,10,30,0.7); 
                                border-radius: 10px; border: 1px solid #ff00ff;">
                        <p style="color: #00ffff; font-family: monospace;">
                            Strings found: """+str(len(strings))+"""
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show raw strings in an expander
                    with st.expander("View raw strings", expanded=False):
                        # Display strings with cyberpunk styling
                        st.markdown("""
                        <div style="height: 300px; overflow-y: auto; background-color: rgba(0,0,20,0.8); 
                                    border-radius: 10px; border: 1px solid #ff00ff; padding: 10px; font-family: monospace;">
                        """, unsafe_allow_html=True)
                        
                        for s in strings:
                            # Generate a random color for each string within cyberpunk palette
                            r = (hash(s) % 100) + 155  # 155-255 range for red
                            g = (hash(s[::-1]) % 100)  # 0-100 range for green
                            b = (hash(s + "salt") % 150) + 105  # 105-255 range for blue
                            
                            st.markdown(f"""
                            <div style="margin-bottom: 8px; border-bottom: 1px solid rgba(255,0,255,0.1); 
                                       padding-bottom: 5px; color: rgb({r},{g},{b});">
                                {s}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No readable strings found in the file.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # File structure analysis with info button
                structure_info = "Analyzes the binary structure of the file to identify potential hidden data sections or anomalies."
                st.markdown(f"### File Structure Analysis {info_button('structure-info', structure_info)}", unsafe_allow_html=True)
                
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                structure = analyze_file_structure(temp_path)
                
                if structure:
                    # Formatted structure output
                    st.markdown("""
                    <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                               border: 1px solid #00ffff; font-family: monospace; height: 200px; 
                               overflow-y: auto; color: #00ffff;">
                    """, unsafe_allow_html=True)
                    
                    for line in structure.split('\n'):
                        if "possible" in line.lower() or "suspect" in line.lower():
                            # Highlight potential findings
                            st.markdown(f"""
                            <div style="color: #ff00ff; font-weight: bold; margin: 5px 0;">
                                {line}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="margin: 3px 0;">
                                {line}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No structure analysis available for this file.")
                
                # Hex dump with info button
                hex_info = "Hexadecimal representation of the file's raw bytes, useful for detecting patterns or anomalies."
                st.markdown(f"### Hex Dump {info_button('hex-info', hex_info)}", unsafe_allow_html=True)
                
                hex_dump = get_hex_dump(temp_path)
                if hex_dump:
                    formatted_dump = format_hex_dump(hex_dump)
                    st.markdown(formatted_dump, unsafe_allow_html=True)
                else:
                    st.info("Unable to generate hex dump for this file.")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
            # Additional tools in tabs
            st.markdown("### Advanced Tools")
            tabs = st.tabs(["ZSteg Analysis", "LSB Viewer", "Bit Plane Analysis", "Detection Details"])
            
            # ZSteg Analysis tab (for PNG files)
            with tabs[0]:
                zsteg_info = "ZSteg is specialized for PNG file analysis and can detect various steganography techniques."
                st.markdown(f"## ZSteg Analysis {info_button('zsteg-info', zsteg_info)}", unsafe_allow_html=True)
                
                if file_type == 'png':
                    try:
                        zsteg_result = run_zsteg(temp_path)
                        if zsteg_result:
                            # Display zsteg results with cyberpunk styling
                            st.markdown("""
                            <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                                      border: 1px solid #00ffff; font-family: monospace; height: 300px; 
                                      overflow-y: auto; color: #00ffff;">
                            """, unsafe_allow_html=True)
                            
                            for line in zsteg_result.split('\n'):
                                # Colorize based on content
                                if "text:" in line or "ascii:" in line:
                                    color = "#ffff00"  # Yellow for text
                                elif "imagedata:" in line or "file:" in line:
                                    color = "#ff00ff"  # Magenta for detected files
                                else:
                                    color = "#00ffff"  # Cyan for other info
                                    
                                st.markdown(f"""
                                <div style="color: {color}; margin: 3px 0;">
                                    {line}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("No results from ZSteg analysis.")
                    except Exception as e:
                        st.error(f"ZSteg analysis error: {str(e)}")
                else:
                    st.info("ZSteg analysis is only available for PNG files.")
            
            # LSB Viewer tab
            with tabs[1]:
                lsb_info = "Least Significant Bit (LSB) viewer shows the least significant bits of each color channel, which are often used to hide data."
                st.markdown(f"## LSB Viewer {info_button('lsb-info', lsb_info)}", unsafe_allow_html=True)
                
                st.info("LSB Viewer will be available in the next update.")
                
                st.markdown("""
                <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                            border: 1px solid #ff00ff; text-align: center;">
                    <p style="color: #00ffff; font-family: monospace;">
                        DEEP ANAL Pro feature coming soon
                    </p>
                    <div style="width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; 
                                background-color: rgba(0,0,20,0.5); border-radius: 5px; margin-top: 10px;">
                        <p style="color: #ff00ff; font-family: monospace; font-size: 1.2em;">
                            LSB VISUALIZATION MATRIX
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Bit Plane Analysis tab
            with tabs[2]:
                bit_plane_info = "Bit plane analysis separates the image into its binary bit planes to reveal patterns invisible in the normal image."
                st.markdown(f"## Bit Plane Analysis {info_button('bit-plane-info', bit_plane_info)}", unsafe_allow_html=True)
                
                st.info("Bit Plane Analysis will be available in the next update.")
                
                st.markdown("""
                <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                            border: 1px solid #ff00ff; text-align: center;">
                    <p style="color: #00ffff; font-family: monospace;">
                        DEEP ANAL Pro feature coming soon
                    </p>
                    <div style="width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; 
                                background-color: rgba(0,0,20,0.5); border-radius: 5px; margin-top: 10px;">
                        <p style="color: #ff00ff; font-family: monospace; font-size: 1.2em;">
                            BIT PLANE MATRIX
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Detection Details tab
            with tabs[3]:
                details_info = "Detailed breakdown of detection algorithms and their findings, with explanation of how the detection score was calculated."
                st.markdown(f"## Detection Details {info_button('details-info', details_info)}", unsafe_allow_html=True)
                
                if detection_result:
                    # Show detailed indicators with explanations
                    st.markdown("""
                    <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                                border: 1px solid #00ffff;">
                        <h3 style="color: #ff00ff; font-family: monospace; margin-bottom: 15px;">
                            Detection Indicators
                        </h3>
                    """, unsafe_allow_html=True)
                    
                    # Create a sorted list of indicators by their value
                    sorted_indicators = sorted(
                        detection_result.indicators.items(),
                        key=lambda x: x[1]['value'],
                        reverse=True
                    )
                    
                    for name, data in sorted_indicators:
                        # Determine color based on value
                        value = data['value']
                        if value > 0.7:
                            ind_color = "#ff0000"  # Red for high values
                        elif value > 0.4:
                            ind_color = "#ffff00"  # Yellow for medium values
                        else:
                            ind_color = "#00ff00"  # Green for low values
                            
                        st.markdown(f"""
                        <div style="margin-bottom: 15px; border-bottom: 1px solid rgba(0,255,255,0.2); padding-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: #00ffff; font-family: monospace; font-weight: bold;">
                                    {name.replace('_', ' ').title()}
                                </span>
                                <span style="color: {ind_color}; font-family: monospace; font-weight: bold;">
                                    {value:.4f}
                                </span>
                            </div>
                            <div style="color: #ffffff; font-family: monospace; font-size: 0.9em; margin-left: 15px;">
                                {data.get('explanation', 'No explanation available')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Show potential techniques
                    st.markdown("""
                    <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                                border: 1px solid #ff00ff; margin-top: 20px;">
                        <h3 style="color: #ff00ff; font-family: monospace; margin-bottom: 15px;">
                            Suspected Steganography Techniques
                        </h3>
                    """, unsafe_allow_html=True)
                    
                    if hasattr(detection_result, "techniques") and detection_result.techniques:
                        for technique in detection_result.techniques:
                            st.markdown(f"""
                            <div style="margin-bottom: 10px; padding: 10px; border-radius: 5px; 
                                       background-color: rgba(80,0,160,0.3); border: 1px solid rgba(255,0,255,0.3);">
                                <span style="color: #ffff00; font-family: monospace; font-weight: bold;">
                                    {technique}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="padding: 10px; text-align: center; color: #ffffff; font-family: monospace;">
                            No specific techniques identified
                        </div>
                        """, unsafe_allow_html=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Show full explanation
                    st.markdown("""
                    <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
                                border: 1px solid #00ffff; margin-top: 20px;">
                        <h3 style="color: #ff00ff; font-family: monospace; margin-bottom: 15px;">
                            Analysis Explanation
                        </h3>
                        <div style="color: #ffffff; font-family: monospace; line-height: 1.5;">
                            {explanation}
                        </div>
                    </div>
                    """.format(explanation=detection_result.generate_explanation()), unsafe_allow_html=True)
                    
                else:
                    st.info("No detection details available.")
        else:
            st.warning("Current version only supports analysis of PNG and JPEG image files.")
            
    except Exception as e:
        st.error(f"Error analyzing file: {str(e)}")
    
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except:
            pass

# Display footer with version info
st.markdown("""
<div style="position: fixed; bottom: 0; right: 0; padding: 5px 10px; 
           background-color: rgba(0,0,20,0.8); border-top-left-radius: 10px;
           border-left: 1px solid #ff00ff; border-top: 1px solid #ff00ff; z-index: 1000;">
    <span style="color: #00ffff; font-family: monospace; font-size: 0.8em;">
        DEEP ANAL v1.0 | {date}
    </span>
</div>
""".format(date=datetime.datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)