import streamlit as st
from streamlit.components.v1 import html

# Read the HTML file
with open("index.html", "r") as file:
    html_content = file.read()

# Set page configuration for better display
st.set_page_config(page_title="Company Information Blocks", layout="wide")

# Render the HTML content
html(html_content, height=800, scrolling=True)