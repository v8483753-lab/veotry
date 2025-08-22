import streamlit as st
import requests
import time

# --- Page Setup ---
st.set_page_config(page_title="Veo Video Generator", layout="centered")
st.title("🎥 Veo Video Generator")
st.markdown("Generate videos using Google's Veo models with live status tracking.")

# --- Inputs ---
api_key = st.text_input("🔑 Enter your Google API Key", type="password")
prompt = st.text_area("📝 Enter your video prompt", placeholder="e.g. a boy dancing in the rain")

# --- Model Selector ---
model = st.radio(
    "🧠 Select Veo Model",
    options=[
        "veo-3.0-generate-preview",
        "veo-3.0-fast-generate-preview",
        "veo-2.0-generate-001"
    ],
    horizontal=True
)

# --- Generate Button ---
if st.button("🚀 Generate Video"):
    if not api_key or not prompt:
        st.error("Please enter both your API key and a prompt.")
        st.stop()

    st.markdown("### 📄 Prompt Preview")
    st.code(prompt)
    st.markdown(f"**Selected Model:** `{model}`")

    # Step 1: Trigger video generation
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning"
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {
            "text": prompt
        }
    }

    try:
        with st.status("⏳ Sending request to Veo API...", expanded=True) as status:
            resp = requests.post(f"{endpoint}?key={api_key}", headers=headers, json=payload)
            if resp.status_code != 200:
                raise ValueError(f"API Error: {resp.status_code} - {resp.text}")

            operation = resp.json()
            operation_name = operation.get("name")
            if not operation_name:
                raise ValueError("No operation name returned from API.")

            status.update(label="✅ Request accepted. Polling for result...", state="running")

        # Step 2: Poll for completion
        poll_url = f"https://generativelanguage.googleapis.com/v1beta/operations/{operation_name}?key={api_key}"
        max_attempts = 20
        for attempt in range(1, max_attempts + 1):
            poll_resp = requests.get(poll_url)
            if poll_resp.status_code != 200:
                raise ValueError(f"Polling Error: {poll_resp.status_code} - {poll_resp.text}")

           
