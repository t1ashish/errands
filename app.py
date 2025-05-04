import streamlit as st
import json
import os

# Path to JSON file
BLOCKS_FILE = "blocks.json"

# Initialize blocks.json if it doesn't exist
def init_blocks():
    if not os.path.exists(BLOCKS_FILE):
        default_blocks = [
            {"name": "", "phone": "", "email": "", "services": "", "rating": 0}
            for _ in range(6)
        ]
        with open(BLOCKS_FILE, "w") as f:
            json.dump({"blocks": default_blocks}, f)

init_blocks()

# Handle API requests
def handle_api():
    query_params = st.experimental_get_query_params()
    action = query_params.get("action", [None])[0]

    if action == "get_blocks":
        try:
            with open(BLOCKS_FILE, "r") as f:
                data = json.load(f)
            st.json(data)
        except Exception as e:
            st.json({"error": str(e)})
        return True

    elif action == "save_block":
        try:
            # Handle POST data (Streamlit doesn't directly support POST, so we use session state)
            if "post_data" in st.session_state:
                request = st.session_state.post_data
                block = request["block"]
                index = request["index"]

                with open(BLOCKS_FILE, "r") as f:
                    data = json.load(f)

                if index is not None and 0 <= index < len(data["blocks"]):
                    data["blocks"][index] = block
                else:
                    data["blocks"].append(block)

                with open(BLOCKS_FILE, "w") as f:
                    json.dump(data, f)

                st.json({"status": "success"})
                del st.session_state.post_data
            else:
                st.json({"error": "No POST data received"})
        except Exception as e:
            st.json({"error": str(e)})
        return True

    return False

# Simulate POST handling via session state
if "post_data" not in st.session_state:
    st.session_state.post_data = None

# Check if this is an API request
if handle_api():
    st.stop()

# Streamlit app
st.set_page_config(page_title="Company Information Directory", layout="wide")

# Render index.html
with open("index.html", "r") as file:
    html_content = file.read()
st.components.v1.html(html_content, height=1000, scrolling=True)

# Handle POST requests via JavaScript (workaround for Streamlit's lack of POST support)
st.markdown("""
<script>
    async function sendPostData(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        window.parent.postMessage({ type: 'streamlit_post', data: await response.json() }, '*');
    }
</script>
""", unsafe_allow_html=True)

# Capture POST data from JavaScript
if st.session_state.post_data is None:
    post_data = st.experimental_get_query_params().get("post_data", [None])[0]
    if post_data:
        try:
            st.session_state.post_data = json.loads(post_data)
        except:
            pass