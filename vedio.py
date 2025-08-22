import streamlit as st
import time

# --- UI Setup ---
st.set_page_config(page_title="Video Generator", layout="centered")
st.title("🎬 AI Video Generator")
st.markdown("Simulate video generation with live status tracking and error handling.")

# --- Input Fields ---
api_key = st.text_input("🔑 Enter your API Key", type="password")
prompt = st.text_area("📝 Enter your video prompt", placeholder="e.g. a boy dancing in the rain")

# --- Generate Button ---
if st.button("🚀 Generate Video"):
    if not api_key or not prompt:
        st.error("Please enter both your API key and a prompt.")
        st.stop()

    st.markdown("### 📄 Prompt Preview")
    st.code(prompt)

    attempt = 1
    max_attempts = 5
    success = False

    while attempt <= max_attempts and not success:
        with st.status(f"⏳ Attempt {attempt}/{max_attempts} — Generating video...", expanded=True) as status:
            try:
                # Simulate API call delay
                time.sleep(2)

                # Simulate error on first attempt
                if attempt == 1:
                    raise ValueError("API key not valid. Please pass a valid API key.")

                # Simulate success
                status.update(label="✅ Video generated successfully!", state="complete")
                st.video("https://www.w3schools.com/html/mov_bbb.mp4")  # Replace with actual video URL
                success = True

            except Exception as e:
                status.update(label=f"❌ Failed (Attempt {attempt})", state="error")
                st.error(f"Error: {str(e)}")
                attempt += 1

                if attempt <= max_attempts:
                    st.info(f"🔁 Retrying in 60 seconds...")
                    time.sleep(3)  # Shortened for demo
                else:
                    st.warning("⚠️ Max attempts reached. Please check your API key or prompt.")
