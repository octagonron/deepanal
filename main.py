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

                if st.button("Close", key="close_detailed", class_name="close-button"):
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
                        st.rerun()
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
                        st.rerun()
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