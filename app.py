import streamlit as st
import google.generativeai as genai
from PIL import Image
import html as html_lib

# ==================== CONFIG ====================
st.set_page_config(
    page_title="my prompties",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.7-flash"

# 🔁 Замените URL, если хотите другую картинку замка
CASTLE_BG_URL = "https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=3840&q=90&auto=format&fit=crop"

# ==================== STYLES ====================
st.markdown(f"""
<style>
    * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}

    /* ========== BASE BACKGROUND ========== */
    html, body, .stApp {{
        background-color: #000000;
        color: #ededed;
    }}
    .stApp {{
        background:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255, 255, 255, 0.05), transparent),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(255, 255, 255, 0.03), transparent),
            #000000;
        background-attachment: fixed;
    }}

    /* ========== CASTLE IMAGE LAYER (behind everything, low opacity) ========== */
    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background-image: url('{CASTLE_BG_URL}');
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        opacity: 0.22;
        pointer-events: none;
        z-index: 0;
        filter: saturate(0.85) brightness(0.9);
    }}

    /* dark vignette to make edges fade into black */
    .stApp::after {{
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.75) 100%);
        pointer-events: none;
        z-index: 0;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(5, 5, 5, 0.65) !important;
        backdrop-filter: blur(24px) saturate(120%);
        -webkit-backdrop-filter: blur(24px) saturate(120%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, div {{ color: #ededed !important; }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1400px;
        position: relative;
        z-index: 1;
    }}

    /* ========== GLASS PANEL ========== */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(180deg, rgba(20, 22, 20, 0.55) 0%, rgba(10, 12, 10, 0.45) 100%) !important;
        backdrop-filter: blur(36px) saturate(130%);
        -webkit-backdrop-filter: blur(36px) saturate(130%);
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow:
            0 1px 0 rgba(255, 255, 255, 0.04) inset,
            0 20px 60px rgba(0, 0, 0, 0.7) !important;
        padding: 20px 22px !important;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 20%;
        right: 20%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.30), transparent);
        pointer-events: none;
    }}

    /* ========== SECTION LABEL ========== */
    .section-label {{
        font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.45) !important;
        padding-bottom: 14px;
        margin-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .section-label::before {{
        content: '';
        width: 5px;
        height: 5px;
        background: #ffffff;
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }}

    /* ========== BUTTONS ========== */
    .stButton > button {{
        width: 100%;
        background: #ffffff;
        color: #000000 !important;
        border: 1px solid #ffffff;
        border-radius: 12px;
        padding: 11px 22px;
        font-weight: 600;
        font-size: 0.86rem;
        letter-spacing: 0.3px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .stButton > button:hover {{
        background: #ffffff;
        border-color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 0 24px rgba(255, 255, 255, 0.25);
    }}
    .stButton > button:active {{ transform: translateY(0); }}
    .stButton > button p, .stButton > button span {{ color: #000000 !important; }}

    /* ========== INPUTS ========== */
    .stTextInput input {{
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 10px !important;
        color: #ededed !important;
        font-size: 0.88rem;
        padding: 10px 14px !important;
        transition: all 0.2s ease;
    }}
    .stTextInput input:focus {{
        border-color: rgba(255, 255, 255, 0.35) !important;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05) !important;
    }}
    .stTextInput input::placeholder {{ color: rgba(237, 237, 237, 0.3) !important; }}

    /* ========== SELECTBOXES ========== */
    .stSelectbox label {{
        font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
        font-size: 0.62rem !important;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        color: rgba(255, 255, 255, 0.4) !important;
        margin-bottom: 4px !important;
    }}
    .stSelectbox div[data-baseweb="select"] > div {{
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 10px !important;
        color: #ededed !important;
        min-height: 38px !important;
        font-size: 0.86rem;
        transition: all 0.2s ease;
    }}
    .stSelectbox div[data-baseweb="select"] > div:hover {{
        border-color: rgba(255, 255, 255, 0.22) !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }}
    div[data-baseweb="popover"] div[role="listbox"] {{
        background: #0a0a0a !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9) !important;
    }}
    div[data-baseweb="popover"] li {{ font-size: 0.86rem !important; }}
    div[data-baseweb="popover"] li:hover {{
        background: rgba(255, 255, 255, 0.06) !important;
    }}

    /* ========== FILE UPLOADER ========== */
    section[data-testid="stFileUploaderDropzone"] {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        min-height: auto !important;
        transition: all 0.2s ease;
    }}
    section[data-testid="stFileUploaderDropzone"]:hover {{
        border-color: rgba(255, 255, 255, 0.3) !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }}
    section[data-testid="stFileUploaderDropzone"] svg {{ fill: rgba(255,255,255,0.5) !important; }}
    section[data-testid="stFileUploaderDropzone"] button {{
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        color: #ededed !important;
        padding: 5px 14px !important;
        font-size: 0.8rem !important;
    }}
    section[data-testid="stFileUploaderDropzone"] button:hover {{
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }}

    /* ========== HIDE STREAMLIT CHROME ========== */
    header[data-testid="stHeader"] {{ background: transparent; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* ============================================================
       ========== COPYABLE TEXT BLOCKS (no nested panel) ==========
       ============================================================ */
    .copyable,
    .result-wrap {{
        background: transparent;
        border: none;
        border-left: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 0;
        padding: 2px 4px 2px 16px;
        margin-top: 18px;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 0.88rem;
        line-height: 1.65;
        white-space: pre-wrap;
        word-break: break-word;
        color: #d8d8d8;
        overflow: hidden;
    }}
    .copyable .hl {{
        color: #ffffff;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.08);
        padding: 1px 6px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.84rem;
    }}

    /* ========== COPY ICON ========== */
    .copy-icon {{
        float: right;
        margin: 0 0 4px 10px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: rgba(255, 255, 255, 0.7);
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
    }}
    .copy-icon:hover {{
        background: rgba(255, 255, 255, 0.14);
        border-color: rgba(255, 255, 255, 0.28);
        color: #ffffff;
    }}
    .copy-icon:active {{ transform: scale(0.92); }}

    /* ========== SIDEBAR CAPTION ========== */
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        color: rgba(255, 255, 255, 0.35) !important;
        letter-spacing: 0.5px;
    }}

    /* ========== SPINNER ========== */
    .stSpinner > div {{
        border-color: rgba(255, 255, 255, 0.15) !important;
        border-top-color: #ffffff !important;
    }}

    /* ========== ALERTS ========== */
    .stAlert {{
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ededed !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

with st.sidebar:
    st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your key…",
        key="gemini_api_key",
        help="Saved for the current session."
    )
    st.caption(f"model // {MODEL_NAME}")

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
    return (
        f'<div class="copyable" id="{block_id}">'
        f'<button class="copy-icon" title="Copy" '
        f'onclick="copyBlock(\'{block_id}\', this)">⧉</button>'
        f'{html_content}'
        f'</div>'
    )

# ==================== OPTIONS ====================
MATERIALS = ["wool", "silk", "suede", "leather"]
ITEM_TYPES = ["blazer", "dress", "coat", "top", "skirt"]
MANNEQUIN_PARTS = ["torso", "-"]
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
    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Generate Description</div>',
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

        if st.button("Generate Description", use_container_width=True, key="gen_btn"):
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
            result_html = (
                f'<div class="result-wrap" id="result-block">'
                f'<button class="copy-icon" title="Copy" '
                f'onclick="copyBlock(\'result-block\', this)">⧉</button>'
                f'{safe}'
                f'</div>'
            )
            st.markdown(result_html, unsafe_allow_html=True)

# ------------------ RIGHT: PROMPTS ------------------
with right:

    # ============ PROMPT 1 ============
    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Prompt / Mannequin</div>',
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

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # ============ PROMPT 2 ============
    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Prompt / Model</div>',
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