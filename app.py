import streamlit as st
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Path to JSON file
BLOCKS_FILE = "blocks.json"

# Initialize blocks.json if it doesn't exist
def init_blocks():
    if not os.path.exists(BLOCKS_FILE):
        default_blocks = [
            {"name": "", "phone": "", "email": "", "services": "", "rating": 0}
            for _ in range(6)
        ]
        try:
            with open(BLOCKS_FILE, "w") as f:
                json.dump({"blocks": default_blocks}, f)
            logger.info("Initialized blocks.json with default blocks")
        except Exception as e:
            logger.error(f"Failed to initialize blocks.json: {str(e)}")

init_blocks()

# Handle API requests
def handle_api():
    query_params = st.query_params
    action = query_params.get("action", None)
    logger.debug(f"Received API request with action: {action}")

    if action == "get_blocks":
        try:
            if not os.path.exists(BLOCKS_FILE):
                init_blocks()
            with open(BLOCKS_FILE, "r") as f:
                data = json.load(f)
            logger.info(f"blocks.json content: {json.dumps(data, indent=2)}")
            logger.info("Successfully fetched blocks")
            st.json(data)
        except Exception as e:
            logger.error(f"Error fetching blocks: {str(e)}")
            st.json({"error": str(e), "blocks": []})
        return True

    elif action == "save_block":
        try:
            logger.debug("Entering save_block handler")
            # Handle POST data via session state
            if "post_data" in st.session_state and st.session_state.post_data:
                request = st.session_state.post_data
                logger.debug(f"Received POST data: {json.dumps(request, indent=2)}")
                block = request["block"]
                index = request["index"]

                # Validate block data
                if not isinstance(block, dict):
                    raise ValueError("Invalid block data")
                required_fields = ["name", "phone", "email", "services", "rating"]
                if not all(field in block for field in required_fields):
                    raise ValueError("Missing required fields")

                # Ensure blocks.json exists
                if not os.path.exists(BLOCKS_FILE):
                    init_blocks()

                # Read current data
                with open(BLOCKS_FILE, "r") as f:
                    data = json.load(f)
                logger.debug(f"Current blocks.json content before save: {json.dumps(data, indent=2)}")

                # Update or append block
                if index is not None and 0 <= index < len(data["blocks"]):
                    data["blocks"][index] = block
                    logger.info(f"Updated block at index {index}")
                else:
                    data["blocks"].append(block)
                    logger.info("Appended new block")

                # Write back to file
                try:
                    with open(BLOCKS_FILE, "w") as f:
                        json.dump(data, f, indent=2)
                    logger.info(f"Successfully saved block to blocks.json: {json.dumps(block, indent=2)}")
                except Exception as e:
                    logger.error(f"Failed to write to blocks.json: {str(e)}")
                    raise e

                st.json({"status": "success"})
                del st.session_state.post_data
            else:
                logger.warning("No POST data received in save_block")
                st.json({"error": "No POST data received"})
        except Exception as e:
            logger.error(f"Error saving block: {str(e)}")
            st.json({"error": str(e)})
        return True

    elif action == "debug_blocks":
        try:
            if not os.path.exists(BLOCKS_FILE):
                init_blocks()
            with open(BLOCKS_FILE, "r") as f:
                data = json.load(f)
            logger.info(f"Debug blocks.json content: {json.dumps(data, indent=2)}")
            st.json({"status": "success", "blocks": data["blocks"]})
        except Exception as e:
            logger.error(f"Error debugging blocks: {str(e)}")
            st.json({"error": str(e), "blocks": []})
        return True

    return False

# Initialize session state
if "post_data" not in st.session_state:
    st.session_state.post_data = None

# Check if this is an API request
if handle_api():
    st.stop()

# Streamlit app
st.set_page_config(page_title="Company Information Directory", layout="wide")

# Render index.html
try:
    with open("index.html", "r") as file:
        html_content = file.read()
    logger.info("Successfully loaded index.html")
    st.components.v1.html(html_content, height=1000, scrolling=True)
except Exception as e:
    logger.error(f"Error loading index.html: {str(e)}")
    st.error("Failed to load the application. Please check the logs.")

# Handle POST requests via JavaScript
st.markdown("""
<script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'streamlit_set_post_data') {
            console.log('Streamlit: Received post data', event.data.data);
            fetch(window.location.href, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event.data.data)
            }).then(response => response.json()).then(data => {
                console.log('Streamlit: POST response', data);
                window.parent.postMessage({ type: 'streamlit_post', data: data }, '*');
            }).catch(error => {
                console.error('Streamlit: POST error', error);
            });
        }
    });

    async function sendPostData(url, data) {
        console.log('Streamlit: Sending post data to', url, data);
        window.parent.postMessage({ type: 'streamlit_set_post_data', data: data }, '*');
    }
</script>
""", unsafe_allow_html=True)

# Capture POST data from JavaScript
if st.session_state.post_data is None:
    post_data = st.query_params.get("post_data", None)
    if post_data:
        try:
            st.session_state.post_data = json.loads(post_data)
            logger.debug(f"Captured POST data from query params: {json.dumps(st.session_state.post_data, indent=2)}")
        except Exception as e:
            logger.error(f"Error parsing POST data: {str(e)}")