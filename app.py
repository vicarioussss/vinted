import streamlit as st
import google.generativeai as genai
from PIL import Image
import html as html_lib

# ==================== CONFIG ====================
st.set_page_config(
    page_title="AI Fashion Description",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.7-flash"

# ==================== GLASSMORPHISM STYLES ====================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(255, 154, 158, 0.40), transparent 45%),
            radial-gradient(circle at 88% 12%, rgba(161, 196, 253, 0.40), transparent 45%),
            radial-gradient(circle at 50% 90%, rgba(186, 156, 255, 0.35), transparent 45%),
            linear-gradient(135deg, #17172a 0%, #23233d 55%, #1b1b2e 100%);
        background-attachment: fixed;
        color: #f4f4fa;
    }
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(18px) saturate(160%);
        -webkit-backdrop-filter: blur(18px) saturate(160%);
        border-right: 1px solid rgba(255, 255, 255, 0.14);
    }
    h1, h2, h3, h4, p, span, label, div { color: #f4f4fa !important; }

    /* Compact page padding */
    .block-container { padding-top: 2rem !important; padding-bottom: 1.5rem !important; max-width: 900px; }

    /* Glass panel */
    .glass {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(18px) saturate(160%);
        -webkit-backdrop-filter: blur(18px) saturate(160%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.30), inset 0 1px 0 rgba(255, 255, 255, 0.18);
        padding: 16px 18px;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        padding: 10px 18px;
        font-weight: 600;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.22);
        transform: translateY(-1px);
        border-color: rgba(255, 255, 255, 0.45);
    }

    /* Inputs */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.20) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1.5px dashed rgba(255, 255, 255, 0.28) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(12px);
        padding: 14px !important;
    }

    /* Hide Streamlit chrome */
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* ---- Result block with copy icon ---- */
    .result-wrap {
        position: relative;
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(22px) saturate(160%);
        -webkit-backdrop-filter: blur(22px) saturate(160%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.20);
        box-shadow: 0 10px 34px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.20);
        padding: 20px 22px;
        margin-top: 10px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.94rem;
        line-height: 1.55;
        color: #f5f5fa;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .copy-icon {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.22);
        color: #f0f0fa;
        border-radius: 8px;
        width: 30px;
        height: 30px;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        transition: all 0.18s ease;
    }
    .copy-icon:hover {
        background: rgba(255, 255, 255, 0.22);
        transform: scale(1.06);
    }
    .copy-icon:active { transform: scale(0.95); }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
# Persist API key in session across reruns
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

with st.sidebar:
    st.markdown("### ✨ AI Fashion Studio")
    st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your key...",
        key="gemini_api_key",
        help="Saved for the current session."
    )
    st.caption("Model: `gemini-3.7-flash`")

# ==================== PROMPT ====================
DESCRIPTION_PROMPT = """You are a professional copywriter for a high-end vintage and designer fashion store.

Analyze the screenshot with garment information and output a product card in EXACTLY the following format. Do NOT add any labels, headings, section titles, or markdown formatting. Do NOT add any introductory or explanatory sentences.

Format (each item on its own line, in this order):

1. A single full product title line in English: brand + composition/material + color + key feature (collar type, cut, etc.) + garment type + size. Example: "Peter Nygård 100% Wool Red Mandarin Collar Blazer – Size 38 / M"

2. One engaging paragraph (3–5 sentences) in English. Describe material, cut, distinctive details (collar, buttons, trims), color, style, season/occasion. Persuasive, editorial tone.

3–6. Four lines in this exact order, each on its own line:
Brand: <brand>
Size: <size> (<measurements if available>)
Material: <composition with percentages, original name in parentheses if present>
Condition: <condition description>

Then ONE blank line.

Last line: 10–15 SEO keywords in lowercase, comma-separated, on a single line. Include brand, material, color, garment type, style, and features.

STRICT RULES:
- Output ONLY the product card. No section labels.
- Only ONE blank line in the entire output — between the Condition line and the keywords.
- No other blank lines anywhere.
- If a field is missing on the screenshot, write "—".
- Everything must be in English.
"""

# ==================== GENERATION ====================
def generate_description(prompt: str, screenshot: Image.Image, api_key: str) -> str | None:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# ==================== MAIN ====================
st.markdown("#### 👗 AI Fashion Description Generator")
st.caption("Upload a product screenshot → get a ready-to-publish description.")

col1, col2 = st.columns([1.15, 1], gap="medium")

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Screenshot",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    screenshot = None
    if uploaded:
        try:
            screenshot = Image.open(uploaded)
            st.image(screenshot, use_container_width=True)
        except Exception as e:
            st.error(f"Cannot open image: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.button("✨ Generate Description", use_container_width=True):
        if not st.session_state["gemini_api_key"]:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif screenshot is None:
            st.error("Please upload a screenshot first.")
        else:
            with st.spinner("Generating..."):
                desc = generate_description(
                    DESCRIPTION_PROMPT,
                    screenshot,
                    st.session_state["gemini_api_key"]
                )
                if desc:
                    st.session_state["description_text"] = desc.strip()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RESULT ====================
if st.session_state.get("description_text"):
    text = st.session_state["description_text"]
    # Escape for HTML, keep line breaks via white-space: pre-wrap
    safe_text = html_lib.escape(text)

    st.markdown(
        f'''
        <div class="result-wrap" id="result-block">
            <button class="copy-icon" title="Copy to clipboard"
                onclick="
                    const t = document.getElementById('result-text').innerText;
                    navigator.clipboard.writeText(t).then(() => {{
                        this.innerText = '✓';
                        setTimeout(() => this.innerText = '⧉', 1400);
                    }});
                ">⧉</button>
            <div id="result-text">{safe_text}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )