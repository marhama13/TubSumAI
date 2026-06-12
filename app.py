import streamlit as st
import ollama
import re
from youtube_transcript_api import YouTubeTranscriptApi

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="TubeSumAI — YouTube Summarizer",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================
# CUSTOM CSS — Light Theme
# =====================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #f5f7ff !important;
    font-family: 'Inter', sans-serif !important;
    color: #111827 !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}
.block-container {
    padding: 2.5rem 1.5rem 4rem !important;
    max-width: 720px !important;
}

/* Input */
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1.5px solid #c9d0e8 !important;
    border-radius: 12px !important;
    color: #111827 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #4f6ef7 !important;
    box-shadow: 0 0 0 3px rgba(79,110,247,0.12) !important;
}
[data-testid="stTextInput"] label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    letter-spacing: 0.05em !important;
}

/* Primary button */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4f6ef7, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    padding: 0.65rem 2rem !important;
    box-shadow: 0 4px 16px rgba(79,110,247,0.30) !important;
    transition: opacity 0.15s, transform 0.15s !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: #fff !important;
    color: #4f6ef7 !important;
    border: 1.5px solid #4f6ef7 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    box-shadow: none !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #eef1ff !important;
    transform: none !important;
}

/* Image */
[data-testid="stImage"] img {
    border-radius: 14px !important;
    box-shadow: 0 8px 32px rgba(79,110,247,0.12) !important;
}

/* Spinner */
[data-testid="stSpinner"] p { color: #6b7280 !important; }

/* Success/warning/error */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# FUNCTIONS
# =====================================

def extract_video_id(url):
    patterns = [
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?]+)",
        r"youtube\.com/embed/([^?]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return " ".join([item.text for item in transcript])

def summarize_with_ollama(transcript):
    prompt = f"""You are an expert YouTube content analyst.

Analyze the transcript and provide:

# Executive Summary

# Key Takeaways
(use bullet points)

# Important Insights

# Action Items

# Conclusion

Transcript:
{transcript[:15000]}
"""
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# =====================================
# HERO
# =====================================

st.markdown("""
<div style="text-align:center; padding: 2rem 0 1.5rem;">
  <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 56 56">
    <rect width="56" height="56" rx="14" fill="#FF0000"/>
    <polygon points="22,18 40,28 22,38" fill="white"/>
  </svg>
  <h1 style="font-family:'Sora',sans-serif; font-size:2.1rem; font-weight:800;
             color:#111827; margin:0.75rem 0 0.4rem; letter-spacing:-0.03em;">
    YouTube <span style="background:linear-gradient(135deg,#4f6ef7,#7c3aed);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Summarizer</span>
  </h1>
  <p style="color:#6b7280; font-size:0.97rem; margin:0; line-height:1.6;">
    Paste any YouTube URL and get an AI summary — powered by Llama 3.2, runs locally.
  </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================
# INPUT
# =====================================

youtube_url = st.text_input(
    "YOUTUBE URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

col1, col2 = st.columns([0.38, 0.62])
with col1:
    generate = st.button("▶  Generate Summary", use_container_width=True)

# =====================================
# RESULT
# =====================================

if generate:
    if not youtube_url.strip():
        st.warning("Paste a YouTube URL above to get started.")
        st.stop()

    try:
        video_id = extract_video_id(youtube_url)

        if not video_id:
            st.error("Invalid YouTube URL. Check the link and try again.")
            st.stop()

        st.divider()

        # Thumbnail
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        st.image(thumbnail_url, use_container_width=True)

        # Transcript
        with st.spinner("Fetching transcript…"):
            transcript = get_transcript(video_id)
        st.success("✓ Transcript loaded")

        # Summary
        with st.spinner("Thinking with Llama 3.2…"):
            summary = summarize_with_ollama(transcript)
        st.success("✦ Summary ready")

        # Render summary
        st.markdown("---")
        st.markdown(summary)
        st.markdown("---")

        # Download
        st.download_button(
            label="📥  Download Summary",
            data=summary,
            file_name="youtube_summary.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")

# =====================================
# HOW IT WORKS
# =====================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:0.72rem; font-weight:700; "
    "letter-spacing:0.12em; text-transform:uppercase; color:#9ca3af; margin-bottom:1rem;'>"
    "HOW IT WORKS</p>",
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

card_style = (
    "background:#ffffff; border:1px solid #e4e8f5; border-radius:16px; "
    "padding:1.6rem 1.2rem; text-align:center; height:100%;"
)

with c1:
    st.markdown(f"""
    <div style="{card_style}">
      <div style="font-size:2rem; margin-bottom:0.75rem;">🔗</div>
      <p style="font-weight:700; font-size:0.95rem; color:#111827; margin:0 0 0.4rem;">Paste URL</p>
      <p style="font-size:0.82rem; color:#6b7280; margin:0; line-height:1.55;">
        Any YouTube link works — tutorials, talks, podcasts
      </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div style="{card_style}">
      <div style="font-size:2rem; margin-bottom:0.75rem;">📜</div>
      <p style="font-weight:700; font-size:0.95rem; color:#111827; margin:0 0 0.4rem;">Extract Transcript</p>
      <p style="font-size:0.82rem; color:#6b7280; margin:0; line-height:1.55;">
        Captions are fetched directly from YouTube
      </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div style="{card_style}">
      <div style="font-size:2rem; margin-bottom:0.75rem;">🤖</div>
      <p style="font-weight:700; font-size:0.95rem; color:#111827; margin:0 0 0.4rem;">AI Summary</p>
      <p style="font-size:0.82rem; color:#6b7280; margin:0; line-height:1.55;">
        Llama 3.2 runs locally — zero data sent to the cloud
      </p>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# FOOTER
# =====================================

st.markdown("""
<div style="text-align:center; color:#9ca3af; font-size:0.76rem;
            margin-top:2.5rem; padding-top:1.5rem; border-top:1px solid #e4e8f5;">
  Built with Streamlit + Ollama &nbsp;·&nbsp; Runs 100% locally &nbsp;·&nbsp;
  No API keys &nbsp;·&nbsp; No data leaves your machine
</div>
""", unsafe_allow_html=True)