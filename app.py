import time
import requests
import streamlit as st

# ---------------- CONFIG ----------------
API_KEY = "AIzaSyA4tIL3TxJEBrpmAXMLUfsX9ue4CSR9a4E"  # <-- paste your key here
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "veo-3.0-generate-preview"  # confirmed working

# ---------------- UI ----------------
st.set_page_config(page_title="Veo 3 Video Generator", page_icon="🎥", layout="centered")
st.title("🎥 Veo 3.0 Video Generator")

if not API_KEY or API_KEY.strip() == "" or API_KEY == "YOUR_API_KEY_HERE":
    st.error("Please paste your API key into the code before running.")
    st.stop()

prompt = st.text_area("Enter your video prompt", height=150)

if st.button("Generate Video"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    # STEP 1: Send generation request
    st.info("🚀 Sending request to generate video...")
    start_url = f"{API_BASE}/models/{MODEL}:generateVideo?key={API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        r = requests.post(start_url, json=payload)
        r.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Error starting generation: {e}\n\n{r.text if 'r' in locals() else ''}")
        st.stop()

    result = r.json()
    st.subheader("API Response")
    st.json(result)

    # If API returns a video URL
    video_url = result.get("videoUri") or result.get("videoUrl")
    if video_url:
        st.video(video_url)
    else:
        st.warning("No direct video URL found in response.")
