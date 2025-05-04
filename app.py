import streamlit as st
from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from starlette.responses import FileResponse
from streamlit.web.server.websocket_headers import _get_websocket_headers

# Initialize FastAPI app
app = FastAPI()

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

# Pydantic model for block data
class Block(BaseModel):
    name: str
    phone: str
    email: str
    services: str
    rating: int

class BlockRequest(BaseModel):
    block: Block
    index: int | None

# FastAPI endpoints
@app.get("/api/blocks")
async def get_blocks():
    with open(BLOCKS_FILE, "r") as f:
        return json.load(f)

@app.post("/api/blocks")
async def save_block(request: BlockRequest):
    with open(BLOCKS_FILE, "r") as f:
        data = json.load(f)
    
    if request.index is not None and 0 <= request.index < len(data["blocks"]):
        data["blocks"][request.index] = request.block.dict()
    else:
        data["blocks"].append(request.block.dict())
    
    with open(BLOCKS_FILE, "w") as f:
        json.dump(data, f)
    
    return {"status": "success"}

# Serve index.html
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

# Streamlit app
def run_streamlit():
    st.set_page_config(page_title="Company Information Directory", layout="wide")
    
    # Get FastAPI URL for client-side fetch
    headers = _get_websocket_headers()
    host = headers.get("Host", "localhost:8501")
    api_url = f"http://{host}"
    
    # Render index.html
    with open("index.html", "r") as file:
        html_content = file.read()
    st.components.v1.html(html_content, height=1000, scrolling=True)

if __name__ == "__main__":
    import uvicorn
    # Run FastAPI with Streamlit
    uvicorn.run(app, host="0.0.0.0", port=8501)
else:
    run_streamlit()