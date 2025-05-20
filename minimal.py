import streamlit as st

st.title("DEEP ANAL: Minimal Test")
st.write("This is a minimal test app to verify Streamlit is working correctly.")

st.success("If you can see this, the basic app is working!")

# Add a simple button
if st.button("Click me"):
    st.write("Button was clicked!")