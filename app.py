import streamlit as st
import google.generativeai as genai
from PIL import Image
import html as html_lib

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Fashion Studio",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.7-flash"

# ==================== STYLES ====================
st.markdown("""
<style>
    /* ---------- Background ---------- */
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(80, 120, 65, 0.55), transparent 50%),
            radial-gradient(circle at 88% 20%, rgba(55, 90, 45, 0.55), transparent 55%),
            radial-gradient(circle at 75% 85%, rgba(40, 70, 35, 0.65), transparent 55%),
            radial-gradient(circle at 20% 90%, rgba(90, 140, 70, 0.35), transparent 50%),
            linear-gradient(135deg, #0b130a 0%, #14200f 55%, #091108 100%);
        background-attachment: fixed;
        color: #eef2e6;
    }
    section[data-testid="stSidebar"] {
        background: rgba(210, 230, 195, 0.07) !important;
        backdrop-filter: blur(24px) saturate(140%);
        -webkit-backdrop-filter: blur(24px) saturate(140%);
        border-right: 1px solid rgba(255, 255, 255, 0.10);
    }
    h1, h2, h3, h4, h5, p, span, label, div { color: #eef2e6 !important; }

    .block-container {
        padding-top: 1.6rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1400px;
    }

    /* ---------- Glass panel ---------- */
    .glass {
        background: rgba(215, 230, 200, 0.10);
        backdrop-filter: blur(28px) saturate(160%);
        -webkit-backdrop-filter: blur(28px) saturate(160%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.16);
        padding: 20px 22px;
    }

    /* ---------- Section heading ---------- */
    .section-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 10px;
        margin-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.22);
    }
    .section-heading .hamburger {
        font-size: 15px;
        letter-spacing: -2px;
        opacity: 0.9;
    }
    .section-heading .heading-text {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 2.4px;
        font-weight: 500;
        opacity: 0.95;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.10);
        color: #eef2e6;
        border: 1px solid rgba(255, 255, 255, 0.32);
        border-radius: 999px;
        padding: 10px 22px;
        font-weight: 500;
        font-size: 0.86rem;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.22);
        border-color: rgba(255, 255, 255, 0.55);
        transform: translateY(-1px);
    }

    /* ---------- Inputs ---------- */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 10px !important;
        color: #eef2e6 !important;
    }
    .stTextInput input::placeholder { color: rgba(238, 242, 230, 0.45) !important; }

    /* ---------- Selectboxes (compact) ---------- */
    .stSelectbox label {
        font-size: 0.68rem !important;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        opacity: 0.7;
        margin-bottom: 2px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 10px !important;
        color: #eef2e6 !important;
        min-height: 36px !important;
        font-size: 0.86rem;
    }
    div[data-baseweb="popover"] div[role="listbox"] {
        background: rgba(30, 45, 25, 0.95) !important;
        backdrop-filter: blur(18px);
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* ---------- File uploader ---------- */
    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1.5px dashed rgba(255, 255, 255, 0.26) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(12px);
        padding: 12px !important;
    }
    section[data-testid="stFileUploaderDropzone"] svg { fill: #c8d6b8 !important; }
    section[data-testid="stFileUploaderDropzone"] button {
        background: rgba(255, 255, 255, 0.10) !important;
        border: 1px solid rgba(255, 255, 255, 0.30) !important;
        border-radius: 999px !important;
        color: #eef2e6 !important;
    }

    /* ---------- Hide Streamlit chrome ---------- */
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* ---------- Result / prompt blocks with copy icon ---------- */
    .copyable {
        position: relative;
        background: rgba(215, 230, 200, 0.06);
        backdrop-filter: blur(20px) saturate(160%);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.14);
        padding: 16px 40px 16px 18px;
        margin-top: 10px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.88rem;
        line-height: 1.55;
        white-space: pre-wrap;
        word-break: break-word;
        color: #f0f5e8;
    }
    .copyable .hl {
        color: #b8e08c;
        font-weight: 600;
    }
    .copy-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.20);
        color: #e8eed8;
        border-radius: 7px;
        width: 26px;
        height: 26px;
        cursor: pointer;
        font-size: 12px;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        transition: all 0.15s ease;
    }
    .copy-icon:hover { background: rgba(255, 255, 255, 0.22); }
    .copy-icon:active { transform: scale(0.92); }

    /* ---------- Description result variant ---------- */
    .result-wrap {
        position: relative;
        background: rgba(215, 230, 200, 0.08);
        backdrop-filter: blur(22px) saturate(160%);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        padding: 16px 40px 16px 18px;
        margin-top: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        line-height: 1.55;
        white-space: pre-wrap;
        word-break: break-word;
        color: #f0f5e8;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

with st.sidebar:
    st.markdown("#### 🌿 Settings")
    st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your key…",
        key="gemini_api_key",
        help="Saved for the current session."
    )
    st.caption(f"Model: `{MODEL_NAME}`")

# ==================== HELPERS ====================
COPY_JS = """
<script>
function copyBlock(id, btn) {
    const el = document.getElementById(id);
    const text = el.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const old = btn.innerText;
        btn.innerText = '✓';
        setTimeout(() => btn.innerText = old, 1300);
    });
}
</script>
"""

def render_copyable(html_content: str, block_id: str) -> str:
    """Wrap HTML content in a glass block with a copy icon."""
    return f'''
    <div class="copyable" id="{block_id}">
        <button class="copy-icon" title="Copy"
            onclick="copyBlock('{block_id}', this)">⧉</button>
        {html_content}
    </div>
    '''

# ==================== PROMPTS ====================
MATERIALS = ["wool", "silk", "suede", "leather"]
ITEM_TYPES = ["blazer", "dress", "coat", "top", "skirt"]
MANNEQUIN_PARTS = ["torso", "full body"]
BOTTOM_COLORS = ["black", "white", "beige", "grey"]

# ==================== DESCRIPTION PROMPT ====================
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

def generate_description(prompt: str, screenshot: Image.Image, api_key: str):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# ==================== LAYOUT ====================
st.markdown(COPY_JS, unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")

# ------------------ LEFT: DESCRIPTION ------------------
with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">'
        '<span class="hamburger">≡</span>'
        '<span class="heading-text">Generate Description</span>'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Screenshot",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key="desc_upload"
    )
    screenshot = None
    if uploaded:
        try:
            screenshot = Image.open(uploaded)
            st.image(screenshot, use_container_width=True)
        except Exception as e:
            st.error(f"Cannot open image: {e}")

    if st.button("✨ Generate Description", use_container_width=True, key="gen_btn"):
        if not st.session_state["gemini_api_key"]:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif screenshot is None:
            st.error("Please upload a screenshot first.")
        else:
            with st.spinner("Generating…"):
                desc = generate_description(
                    DESCRIPTION_PROMPT,
                    screenshot,
                    st.session_state["gemini_api_key"]
                )
                if desc:
                    st.session_state["description_text"] = desc.strip()

    if st.session_state.get("description_text"):
        safe = html_lib.escape(st.session_state["description_text"])
        st.markdown(
            f'''
            <div class="result-wrap" id="result-block">
                <button class="copy-icon" title="Copy"
                    onclick="copyBlock('result-block', this)">⧉</button>
                <div>{safe}</div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ RIGHT: PROMPTS ------------------
with right:

    # ============ PROMPT 1 ============
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">'
        '<span class="hamburger">≡</span>'
        '<span class="heading-text">Prompt — Mannequin</span>'
        '</div>',
        unsafe_allow_html=True
    )

    p1c1, p1c2, p1c3 = st.columns(3)
    with p1c1:
        p1_material = st.selectbox("Material", MATERIALS, index=0, key="p1_mat")
    with p1c2:
        p1_item = st.selectbox("Item", ITEM_TYPES, index=0, key="p1_item")
    with p1c3:
        p1_part = st.selectbox("Mannequin", MANNEQUIN_PARTS, index=0, key="p1_part")

    p1_html = (
        f'Generate a high-resolution studio photo of this '
        f'<span class="hl">{p1_material}</span> '
        f'<span class="hl">{p1_item}</span>, '
        f'preserving every detail, on a headless/armless feminine cream linen mannequin '
        f'<span class="hl">{p1_part}</span>, '
        f'turned three-quarters toward the left side of the frame with soft incoming light, '
        f'against a plain dark background'
    )
    st.markdown(render_copyable(p1_html, "prompt1"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # ============ PROMPT 2 ============
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">'
        '<span class="hamburger">≡</span>'
        '<span class="heading-text">Prompt — Model</span>'
        '</div>',
        unsafe_allow_html=True
    )

    p2c1, p2c2, p2c3 = st.columns(3)
    with p2c1:
        p2_material = st.selectbox("Material", MATERIALS, index=0, key="p2_mat")
    with p2c2:
        p2_item = st.selectbox("Item", ITEM_TYPES, index=0, key="p2_item")
    with p2c3:
        p2_bottom = st.selectbox("Trousers", BOTTOM_COLORS, index=0, key="p2_bottom")

    p2_html = (
        f'Fashion e-commerce photography, mid-shot of a model, wearing this '
        f'<span class="hl">{p2_material}</span> '
        f'<span class="hl">{p2_item}</span> and '
        f'<span class="hl">{p2_bottom}</span> high-waist wide-leg trousers. '
        f'Faceless framing, cropped at the chin, casual pose. '
        f'Clean light neutral grey studio background. Soft diffused lighting, minimalist aesthetic, '
        f'effortless chic, high contrast, sharp clothing details, photorealistic '
        f'--ar 3:4 --style raw'
    )
    st.markdown(render_copyable(p2_html, "prompt2"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)