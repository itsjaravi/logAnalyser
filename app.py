import streamlit as st
import os
from dotenv import load_dotenv
import requests
import re

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq API endpoint
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Function to clean <think> blocks from the model output
def clean_model_output(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# Streamlit UI
st.set_page_config(page_title="AI Log Analyzer", layout="centered")
st.title("📊 AI Log Analyzer")
st.markdown("Upload your `.txt` log file and get a detailed AI-driven analysis.")

uploaded_file = st.file_uploader("Upload Log File", type=["txt"])

if uploaded_file is not None:
    log_content = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Log Preview")
    st.text_area("Content", log_content, height=200)

    if st.button("Analyze Logs"):
        with st.spinner("Analyzing logs using AI..."):

            # Construct prompt for Groq model
            prompt = f"""
You are a log analysis assistant. Analyze the following logs in detail:

1. Count the number of errors.
2. Classify the types of errors (e.g., NullPointerException, Timeout, etc.).
3. Identify the frequency and patterns.
4. Summarize warnings or unusual events.
5. Suggest possible root causes and solutions.
6. Highlight any security issues or performance bottlenecks.

Here is the log content:
{log_content}
"""

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "deepseek-r1-distill-llama-70b",
                "messages": [
                    {"role": "system", "content": "You are a senior DevOps AI specialized in log analysis."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "top_p": 1,
                "n": 1,
                "stream": False
            }

            response = requests.post(GROQ_URL, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                cleaned_analysis = clean_model_output(analysis)
                st.subheader("🔍 Detailed AI Analysis")
                st.markdown(cleaned_analysis)
            else:
                st.error(f"Error: {response.status_code}")
                st.json(response.json())
