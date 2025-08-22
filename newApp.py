import time
import requests
import streamlit as st
from datetime import datetime

# ─────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────
API_KEY = "AIzaSyA4tIL3TxJEBrpmAXMLUfsX9ue4CSR9a4E"  # ← paste your key
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "veo-3.0-generate-preview"  # confirmed working

# ─────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Veo 3 Video Generator", page_icon="🎥", layout="centered")
st.title("🎥 Veo 3.0 Video Generator")

if not API_KEY or API_KEY.strip() == "" or API_KEY == "YOUR_API_KEY_HERE":
    st.error("Please paste your API key into the code before running.")
    st.stop()

prompt = st.text_area("Enter your video prompt", height=150, placeholder="A cinematic shot of a futuristic city at sunset, vibrant, 8 seconds")

# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def start_generation(prompt_text: str) -> str:
    url = f"{API_BASE}/models/{MODEL}:predictLongRunning?key={API_KEY}"
    payload = {"instances": [{"prompt": prompt_text}]}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    op_name = data.get("name")
    if not op_name:
        raise RuntimeError("No operation name returned from API.")
    return op_name

def poll_operation(op_name: str, interval_sec: int = 5, max_attempts: int = 120) -> dict:
    url = f"{API_BASE}/{op_name}?key={API_KEY}"
    for attempt in range(1, max_attempts + 1):
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if data.get("done"):
            return data
        st.write(f"⏳ Polling status from server... (Attempt {attempt})")
        time.sleep(interval_sec)
    raise TimeoutError("Video generation timed out. Try again later.")

def extract_video_uri(response_obj: dict) -> str | None:
    try:
        return response_obj["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
    except (KeyError, IndexError, TypeError):
        return None

def with_api_key(url: str, api_key: str) -> str:
    if "key=" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}key={api_key}"

# ─────────────────────────────────────────────────────────
# Action
# ─────────────────────────────────────────────────────────
if st.button("Generate Video"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    # Start generation
    st.info("🚀 Sending request to start video generation...")
    try:
        op_name = start_generation(prompt)
    except requests.RequestException as e:
        st.error(f"Error starting generation: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error starting generation: {e}")
        st.stop()

    st.success(f"✅ Generation started. Operation ID: {op_name}")

    # Poll for completion
    progress = st.progress(0)
    start_time = time.time()
    try:
        # Update a soft progress indicator while polling
        for i in range(100):
            progress.progress(i + 1)
            time.sleep(0.02)
            if i == 99:
                break
        result = poll_operation(op_name, interval_sec=5, max_attempts=120)
    except requests.RequestException as e:
        st.error(f"Error polling status: {e}")
        st.stop()
    except TimeoutError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error while polling: {e}")
        st.stop()

    # Render video (clean UI: no raw JSON)
    response_obj = result.get("response", {})
    video_uri = extract_video_uri(response_obj)

    if not video_uri:
        st.error("Video completed but no URI was returned by the API.")
        st.stop()

    # Build an authenticated URL for playback/download
    direct_url = with_api_key(video_uri, API_KEY)

    st.success("✅ Video ready!")
    # Prefer using the URL so the browser streams directly with key param
    st.video(direct_url)

    # Also fetch bytes to enable a reliable download button
    try:
        file_resp = requests.get(direct_url)
        if file_resp.status_code == 200:
            file_bytes = file_resp.content
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Download Video",
                data=file_bytes,
                file_name=f"generated_video_{ts}.mp4",
                mime="video/mp4",
            )
        else:
            st.warning(f"Video playable, but download failed (HTTP {file_resp.status_code}). Try the player menu.")
    except Exception as e:
        st.warning(f"Video playable, but download encountered an error: {e}")
