import streamlit as st
import requests
import time
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Veo Video Generator", page_icon="🎬")

# Get API key from environment or input
API_KEY = os.getenv("GOOGLE_API_KEY") or st.text_input(
    "Enter your Google API Key", type="password"
)

# Veo API endpoints
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "veo-1.5"  # Change if your account uses a different model

# -----------------------------
# FUNCTIONS
# -----------------------------
def start_video_generation(prompt: str) -> str:
    """Send prompt to Veo API and return operation name."""
    url = f"{API_BASE}/models/{MODEL}:generateVideo?key={API_KEY}"
    payload = {"prompt": {"text": prompt}}
    r = requests.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    return data.get("name")  # Operation name for polling


def poll_operation(operation_name: str, timeout=300, interval=10):
    """Poll until the operation is done or timeout."""
    url = f"{API_BASE}/operations/{operation_name}?key={API_KEY}"
    start_time = time.time()

    while time.time() - start_time < timeout:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        if data.get("done"):
            return data
        time.sleep(interval)

    return {"error": "Timeout waiting for video"}


# -----------------------------
# UI
# -----------------------------
st.title("🎬 Veo Video Generator")

prompt = st.text_area("Enter your cinematic prompt", height=100)

if st.button("Generate Video"):
    if not API_KEY:
        st.error("Please enter your API key.")
    elif not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        try:
            with st.spinner("Starting video generation..."):
                op_name = start_video_generation(prompt)

            with st.spinner("Waiting for video to be ready..."):
                result = poll_operation(op_name)

            if "error" in result:
                st.error(result["error"])
                st.json(result)
            elif "response" in result:
                # Adjust this path if your API returns a different structure
                video_url = (
                    result["response"]
                    .get("video", {})
                    .get("uri")
                )
                if video_url:
                    st.video(video_url)
                else:
                    st.warning("Video generated but no URL found.")
                    st.json(result)
            else:
                st.warning("Unexpected API response.")
                st.json(result)

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
