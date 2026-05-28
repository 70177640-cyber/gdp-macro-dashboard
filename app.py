import streamlit as st

st.title("🚀 My Streamlit Dashboard")

name = st.text_input("Enter your name")

if st.button("Submit"):
    st.success(f"Hello {name}! Your Streamlit app is running 🎉")