import streamlit as st
import tempfile
import os
import json
import datetime
from pathlib import Path
from utils.file_analysis import (
    get_file_metadata, extract_strings, analyze_file_structure,
    calculate_entropy, get_byte_frequency, get_hex_dump
)
from utils.visualizations import (
    create_entropy_plot, create_byte_frequency_plot, format_hex_dump,
    create_detailed_view
)
from utils.database import (
    save_analysis, get_recent_analyses, get_analysis_by_id
)
from utils.stego_detector import analyze_image_for_steganography
from utils.stego_decoder import brute_force_decode

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

# Initialize session state
if 'show_detailed_view' not in st.session_state:
    st.session_state.show_detailed_view = None
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'selected_history_id' not in st.session_state:
    st.session_state.selected_history_id = None

# Sidebar for database operations
with st.sidebar:
    st.markdown("""
    <div style="text-align: center;">
        <h3 style="color: #00ffff; font-family: monospace; margin-bottom: 20px;">
            DEEP ANAL DATABASE
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle between upload and history views
    view_options = ["🔍 New Analysis", "💾 Analysis History"]
    selected_view = st.selectbox("Select View", view_options, key="view_selector")
    
    if selected_view == "💾 Analysis History":
        st.session_state.view_history = True
        
        # Get recent analyses from database
        analyses = get_recent_analyses(limit=20)
        
        if analyses:
            st.markdown("""
            <div style="border: 1px solid #00ffff; padding: 10px; border-radius: 5px; 
                        background-color: rgba(0,0,20,0.8); margin-bottom: 15px;">
                <h4 style="color: #ff00ff; font-family: monospace;">Recent Analyses</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for analysis in analyses:
                # Format date for display
                date_str = analysis.analysis_date.strftime("%Y-%m-%d %H:%M")
                
                # Create a card for each analysis
                card = f"""
                <div style="margin-bottom: 10px; padding: 8px; border-radius: 5px; background: rgba(0,10,30,0.4);
                            border-left: 3px solid #00ffff; cursor: pointer;"
                     onclick="this.style.borderColor='#ff00ff';">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #00ffff; font-family: monospace; font-size: 0.9em; white-space: nowrap; 
                                    overflow: hidden; text-overflow: ellipsis; max-width: 150px;">
                            {analysis.filename}
                        </span>
                        <span style="color: #ffff00; font-family: monospace; font-size: 0.8em;">
                            {date_str}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color: #ff00ff; font-family: monospace; font-size: 0.8em;">
                            Type: {analysis.file_type or 'Unknown'}
                        </span>
                        <span style="color: #00ffff; font-family: monospace; font-size: 0.8em;">
                            Entropy: {analysis.entropy_value:.2f}
                        </span>
                    </div>
                </div>
                """
                
                # Use a button with the card UI inside it
                if st.markdown(card, unsafe_allow_html=True):
                    st.session_state.selected_history_id = analysis.id
                
                # Add a small button for loading this analysis
                if st.button(f"Load #{analysis.id}", key=f"load_{analysis.id}"):
                    st.session_state.selected_history_id = analysis.id
                    st.info(f"Loading analysis #{analysis.id}")
    else:
        st.session_state.view_history = False
        
        st.markdown("""
        <div style="border: 1px solid #00ffff; padding: 10px; border-radius: 5px; 
                    background-color: rgba(0,0,20,0.8); margin-bottom: 15px;">
            <h4 style="color: #ff00ff; font-family: monospace;">Welcome to DEEP ANAL</h4>
            <p style="color: #00ffff; font-family: monospace; font-size: 0.9em;">
                Upload an image file to begin analysis.
            </p>
            <p style="color: #ffff00; font-family: monospace; font-size: 0.8em;">
                Analysis results will be saved to the database for future reference.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display system status
        st.markdown("""
        <div style="border: 1px solid #ff00ff; padding: 10px; border-radius: 5px; 
                    background-color: rgba(0,0,20,0.8); margin-top: 20px;">
            <h4 style="color: #00ffff; font-family: monospace;">System Status</h4>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span style="color: #ffff00; font-family: monospace; font-size: 0.8em;">
                    Database
                </span>
                <span style="color: #00ffff; font-family: monospace; font-size: 0.8em;">
                    ONLINE
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span style="color: #ffff00; font-family: monospace; font-size: 0.8em;">
                    Analysis Engine
                </span>
                <span style="color: #00ffff; font-family: monospace; font-size: 0.8em;">
                    READY
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span style="color: #ffff00; font-family: monospace; font-size: 0.8em;">
                    Visualization Core
                </span>
                <span style="color: #00ffff; font-family: monospace; font-size: 0.8em;">
                    ACTIVE
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Main content
if st.session_state.view_history and st.session_state.selected_history_id:
    # Display the selected analysis from history
    analysis = get_analysis_by_id(st.session_state.selected_history_id)
    
    if analysis:
        st.markdown(f"""
        <div style="border: 2px solid #00ffff; padding: 15px; border-radius: 10px; 
                    background-color: rgba(0,0,20,0.8); margin-bottom: 20px;">
            <h2 style="color: #ff00ff; font-family: monospace;">
                Analysis History: {analysis.filename}
            </h2>
            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                <span style="color: #00ffff; font-family: monospace;">
                    Date: {analysis.analysis_date.strftime("%Y-%m-%d %H:%M:%S")}
                </span>
                <span style="color: #ff00ff; font-family: monospace;">
                    Type: {analysis.file_type}
                </span>
                <span style="color: #ffff00; font-family: monospace;">
                    Entropy: {analysis.entropy_value:.4f}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stored File Analysis")
            
            # Metadata
            with st.expander("📋 File Metadata", expanded=True):
                try:
                    metadata = json.loads(analysis.meta_data)
                    for key, value in metadata.items():
                        st.markdown(f"**{key}:** {value}")
                except:
                    st.write("No metadata available or invalid format")
            
            # File size and type
            with st.expander("📊 File Information", expanded=True):
                st.markdown(f"**File Size:** {analysis.file_size} bytes")
                st.markdown(f"**File Type:** {analysis.file_type}")
                st.markdown(f"**Analysis Date:** {analysis.analysis_date}")
        
        with col2:
            st.subheader("Entropy Visualization")
            
            # Show entropy visualization based on stored value
            st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
            st.plotly_chart(
                create_entropy_plot(analysis.entropy_value),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Option to clear history view
            if st.button("Back to File Upload", key="back_button"):
                st.session_state.view_history = False
                st.session_state.selected_history_id = None
                st.rerun()
    else:
        st.error("Analysis not found in database")
        if st.button("Return to Upload"):
            st.session_state.view_history = False
            st.session_state.selected_history_id = None
            st.rerun()
else:
    # Regular file upload view
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

                close_col1, close_col2, close_col3 = st.columns([1, 3, 1])
                with close_col1:
                    if st.button("Close", key="close_detailed"):
                        st.session_state.show_detailed_view = None
                        st.rerun()

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
                # Add a prominent stego detection banner at the top
                # Run steganography detection 
                is_image = uploaded_file.type.startswith('image/')
                if is_image:
                    detection_result = analyze_image_for_steganography(temp_path)
                    likelihood_percentage = detection_result.get_formatted_likelihood()
                    color_code = detection_result.get_color_code()
                    
                    # Display a prominent banner showing the likelihood
                    banner_html = f"""
                    <div style="margin-bottom: 25px; padding: 15px; border-radius: 10px; 
                                background: linear-gradient(90deg, rgba(20,0,36,0.8) 0%, rgba(121,9,100,0.8) 100%);
                                border: 2px solid {color_code}; box-shadow: 0 0 20px {color_code};">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <h2 style="margin: 0; color: #ffffff; font-family: 'Courier New', monospace; text-shadow: 0 0 10px {color_code};">
                                    STEGANOGRAPHY DETECTION RESULT
                                </h2>
                                <p style="margin: 5px 0 0 0; color: #cccccc; font-family: 'Courier New', monospace;">
                                    Deep analysis complete. Hidden data assessment:
                                </p>
                            </div>
                            <div style="text-align: center; background: rgba(0,0,0,0.3); padding: 10px 20px; 
                                        border-radius: 8px; border: 1px solid {color_code};">
                                <h1 style="margin: 0; font-size: 2.5rem; color: {color_code}; font-family: 'Courier New', monospace;
                                          text-shadow: 0 0 10px {color_code};">
                                    {likelihood_percentage}
                                </h1>
                                <p style="margin: 0; color: #ffffff; font-size: 0.9rem; font-family: 'Courier New', monospace;">
                                    chance of hidden data
                                </p>
                            </div>
                        </div>
                        <div style="margin-top: 12px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 5px;">
                            <p style="margin: 0; color: #ffffff; font-family: 'Courier New', monospace; font-size: 0.9rem;">
                                {detection_result.main_finding}
                            </p>
                            
                            <div style="margin-top: 10px;">
                                <span style="color: #ff00ff; font-family: 'Courier New', monospace; font-weight: bold;">
                                    Suspected techniques:
                                </span>
                                <span style="color: #00ffff; font-family: 'Courier New', monospace; margin-left: 10px;">
                                    {', '.join(detection_result.techniques) if detection_result.techniques else 'None identified'}
                                </span>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(banner_html, unsafe_allow_html=True)
                
                # Create two columns for the layout
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("File Analysis")

                    # Metadata
                    with st.expander("📋 File Metadata", expanded=True):
                        metadata = get_file_metadata(temp_path)
                        for key, value in metadata.items():
                            st.markdown(f"**{key}:** {value}")
                        
                        # Save analysis to database
                        try:
                            # Get file size
                            file_size = os.path.getsize(temp_path)
                            
                            # Get file type
                            file_type = metadata.get('File Type', 'Unknown')
                            
                            # Convert metadata to JSON string
                            metadata_json = json.dumps(metadata)
                            
                            # Save to database
                            analysis_id = save_analysis(
                                filename=uploaded_file.name,
                                file_size=file_size,
                                file_type=file_type,
                                entropy_value=calculate_entropy(temp_path),
                                metadata=metadata_json
                            )
                            
                            # Display success message
                            st.success(f"Analysis saved to database with ID: {analysis_id}")
                        except Exception as e:
                            st.error(f"Failed to save analysis to database: {str(e)}")

                    # String Analysis
                    with st.expander("🔤 String Analysis", expanded=True):
                        strings = extract_strings(temp_path)
                        st.code("\n".join(strings[:100]))

                    # File Structure
                    with st.expander("📁 File Structure", expanded=True):
                        structure = analyze_file_structure(temp_path)
                        st.code(structure)
                    
                    # Steganography Detection Details
                    if is_image:
                        with st.expander("🔍 Steganography Detection Details", expanded=True):
                            # Create table with all the detection indicators
                            st.markdown("### Detection Indicators")
                            
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
                                if value < 0.3:
                                    value_color = "#00ff00"  # Green for low likelihood
                                elif value < 0.7:
                                    value_color = "#ffff00"  # Yellow for medium likelihood
                                else:
                                    value_color = "#ff0000"  # Red for high likelihood
                                
                                st.markdown(f"""
                                <div style="display: grid; grid-template-columns: 3fr 1fr 1fr; gap: 10px; margin-bottom: 5px; 
                                            background: rgba(0,0,0,0.1); padding: 8px; border-radius: 3px;">
                                    <div style="color: #ffffff; font-family: monospace;">{name}</div>
                                    <div style="color: {value_color}; font-family: monospace; font-weight: bold;">{value*100:.1f}%</div>
                                    <div style="color: #00ffff; font-family: monospace;">{weight}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Display full explanation
                            st.markdown("### Detailed Explanation")
                            
                            explanation_html = f"""
                            <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; 
                                        border-left: 3px solid {color_code}; margin-top: 10px;">
                                <p style="color: #ffffff; font-family: monospace;">
                                    {detection_result.main_finding}
                                </p>
                                
                                <div style="margin-top: 15px;">
                                    <p style="color: #00ffff; font-family: monospace; font-weight: bold;">Specific findings:</p>
                                    <ul style="list-style-type: none; padding-left: 5px;">
                            """
                            
                            # Add the detailed findings
                            for finding in detection_result.detailed_findings:
                                explanation_html += f"""
                                        <li style="color: #ffffff; font-family: monospace; margin-bottom: 5px;">
                                            • {finding}
                                        </li>
                                """
                                
                            explanation_html += """
                                    </ul>
                                </div>
                            </div>
                            """
                            
                            st.markdown(explanation_html, unsafe_allow_html=True)

                with col2:
                    st.subheader("Visualizations")

                    # Entropy Analysis
                    entropy = calculate_entropy(temp_path)
                    st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                    st.plotly_chart(
                        create_entropy_plot(entropy, lower_staging=True),
                        use_container_width=True
                    )
                    if st.button("View Detailed Entropy Analysis", key="entropy_detail"):
                        st.session_state.show_detailed_view = "entropy"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Byte Frequency
                    bytes_values, frequencies = get_byte_frequency(temp_path)
                    st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                    st.plotly_chart(
                        create_byte_frequency_plot(bytes_values, frequencies, lower_staging=True),
                        use_container_width=True
                    )
                    if st.button("View Detailed Frequency Analysis", key="frequency_detail"):
                        st.session_state.show_detailed_view = "frequency"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Hex Dump
                    with st.expander("📝 Hex Dump", expanded=True):
                        hex_dump = get_hex_dump(temp_path)
                        st.markdown(format_hex_dump(hex_dump), unsafe_allow_html=True)
                    
                    # Brute Force Decoder for images
                    if is_image and detection_result.likelihood > 0.3:
                        with st.expander("⚡ Steganography Decoder", expanded=True):
                            st.markdown("""
                            <h3 style="color: #00ffff; font-family: monospace; margin-bottom: 10px;">
                                Automated Brute-Force Decoder
                            </h3>
                            <p style="color: #ffffff; font-family: monospace; margin-bottom: 15px;">
                                Attempt to extract hidden data using multiple steganography methods.
                            </p>
                            """, unsafe_allow_html=True)
                            
                            # Password list for brute force
                            st.markdown('<div style="margin-bottom: 10px;">', unsafe_allow_html=True)
                            password_input = st.text_input(
                                "Optional password list (comma-separated)",
                                placeholder="password,123456,admin,stego,secret",
                                key="password_list"
                            )
                            
                            # Convert input to list if provided
                            password_list = None
                            if password_input:
                                password_list = [p.strip() for p in password_input.split(",") if p.strip()]
                            
                            # Run the decoder
                            if st.button("Run Brute-Force Decoder", key="run_decoder"):
                                with st.spinner("Running brute-force decoding... This may take some time."):
                                    results = brute_force_decode(temp_path, password_list)
                                    
                                    # Display results
                                    for i, result in enumerate(results):
                                        if result.success:
                                            # Display successful result with higher prominence
                                            st.markdown(f"""
                                            <div style="margin-bottom: 15px; padding: 12px; border-radius: 5px; 
                                                        background: linear-gradient(90deg, rgba(0,36,23,0.8) 0%, rgba(9,121,75,0.8) 100%);
                                                        border: 2px solid #00ff00;">
                                                <h4 style="margin: 0; color: #00ff00; font-family: monospace;">
                                                    ✅ SUCCESS: {result.method}
                                                </h4>
                                                <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                                                    <span style="color: #ffffff; font-family: monospace;">
                                                        Confidence: {result.confidence*100:.1f}%
                                                    </span>
                                                    <span style="color: #00ffff; font-family: monospace;">
                                                        Data size: {len(result.data) if result.data else 0} bytes
                                                    </span>
                                                </div>
                                                
                                                <div style="margin-top: 10px; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px;">
                                                    <p style="color: #00ff00; font-family: monospace; margin-bottom: 5px; font-weight: bold;">
                                                        Data Preview:
                                                    </p>
                                                    <code style="color: #ffffff; font-family: monospace; white-space: pre-wrap; display: block; 
                                                              word-break: break-all; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 3px;">
                                                        {str(result.data[:1000]).replace('<', '&lt;').replace('>', '&gt;') if result.data else 'No data'}
                                                    </code>
                                                </div>
                                                
                                                <div style="margin-top: 8px;">
                                                    <span style="color: #00ffff; font-family: monospace; font-weight: bold;">
                                                        Additional Info:
                                                    </span>
                                                    <span style="color: #ffffff; font-family: monospace; margin-left: 5px;">
                                                        {', '.join(f"{k}={v}" for k, v in result.info.items())}
                                                    </span>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            # Just list the unsuccessful methods more compactly
                                            st.markdown(f"""
                                            <div style="margin-bottom: 8px; padding: 8px; border-radius: 4px; 
                                                        background: rgba(0,0,0,0.2); border-left: 3px solid #ff0000;">
                                                <div style="display: flex; justify-content: space-between;">
                                                    <span style="color: #ff0000; font-family: monospace;">
                                                        ❌ Failed: {result.method}
                                                    </span>
                                                    <span style="color: #ffffff; font-family: monospace;">
                                                        {', '.join(f"{k}={v}" for k, v in result.info.items() if k == 'error')}
                                                    </span>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)

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