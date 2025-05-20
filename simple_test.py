import streamlit as st

st.title("DEEP ANAL Simple Test")
st.success("If you can see this, the application is working correctly!")

# Create a simple button
if st.button("Click me for cyberpunk"):
    st.markdown("""
    <div style="background-color: rgba(0,10,30,0.7); padding: 15px; border-radius: 10px; 
               border: 1px solid #ff00ff; text-align: center;">
        <h2 style="color: #ff00ff; font-family: monospace;">
            DEEP ANAL IS OPERATIONAL
        </h2>
    </div>
    """, unsafe_allow_html=True)