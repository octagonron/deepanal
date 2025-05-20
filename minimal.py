import streamlit as st

st.title("DEEP ANAL: Steganography Analysis")
st.write("Minimal test app")

# File upload
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.write(f"Filename: {uploaded_file.name}")
    st.image(uploaded_file, caption=uploaded_file.name)
else:
    st.write("Please upload an image file")