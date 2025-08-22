import time
import requests
import streamlit as st

# ---------------- CONFIG ----------------
API_KEY = "AIzaSyA4tIL3TxJEBrpmAXMLUfsX9ue4CSR9a4E"  # <-- paste your key here
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "veo-3.0-generate-preview"

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

    # STEP 1: Start generation
    st.info("🚀 Sending request to start video generation...")
    start_url = f"{API_BASE}/models/{MODEL}:predictLongRunning?key={API_KEY}"
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ]
    }

    try:
        r = requests.post(start_url, json=payload)
        r.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Error starting generation: {e}\n\n{r.text if 'r' in locals() else ''}")
        st.stop()

    operation = r.json()
    operation_name = operation.get("name")
    if not operation_name:
        st.error("No operation name returned. Cannot poll status.")
        st.json(operation)
        st.stop()

    st.success(f"✅ Generation started. Operation ID: {operation_name}")

    # STEP 2: Poll until done
    status_url = f"{API_BASE}/{operation_name}?key={API_KEY}"
    progress_bar = st.progress(0)
    poll_count = 0

    while True:
        poll_count += 1
        try:
            status_resp = requests.get(status_url)
            status_resp.raise_for_status()
        except requests.RequestException as e:
            st.error(f"Error polling status: {e}")
            st.stop()

        status_data = status_resp.json()
        done = status_data.get("done", False)

        progress_bar.progress(min(poll_count * 5, 100))

        if done:
            st.success("🎉 Video generation complete!")
            break

        st.write(f"⏳ Polling status from server... (Attempt {poll_count})")
        time.sleep(5)

    # STEP 3: Show result
    if "response" in status_data:
        video_info = status_data["response"]
        st.subheader("Video Generation Response")
        st.json(video_info)

        # Extract video URL from nested structure
        try:
            raw_url = video_info["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
            # Append API key for direct access
            if "?alt=media" in raw_url:
                video_url = f"{raw_url}&key={API_KEY}"
            else:
                video_url = f"{raw_url}?key={API_KEY}"
        except (KeyError, IndexError, TypeError):
            video_url = None

        if video_url:
            st.success("✅ Video ready! Fetching file...")

            video_resp = requests.get(video_url)
            if video_resp.status_code == 200:
                video_bytes = video_resp.content

                # Play video inline
                st.video(video_bytes)

                # Download button
                st.download_button(
                    label="📥 Download Video",
                    data=video_bytes,
                    file_name="generated_video.mp4",
                    mime="video/mp4"
                )
            else:
                st.error(f"Failed to fetch video file: {video_resp.status_code}")
        else:
            st.warning("No video URL found in response.")
    else:
        st.error("No 'response' field in final status.")
        st.json(status_data)
