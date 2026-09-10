import streamlit as st
import google.generativeai as genai
from PIL import Image
import html as html_lib
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import requests
import io
import json
import time
import os

WHITE_MOON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E"
    "%3Cpath fill='%23ffffff' d='M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z'/%3E"
    "%3C/svg%3E"
)

st.set_page_config(
    page_title="my prompties",
    page_icon=WHITE_MOON,
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.7-flash"
LEONARDO_API = "https://cloud.leonardo.ai/api/rest/v1"
LEONARDO_MODEL = "b24e16ff-06e3-43eb-8d33-4416c2d75876"
LEONARDO_DEFAULT_TOKEN = "cfut_bMc1ubiicg6g83noA0GnvbUhn1PHRtsVRG9PfMFEa5486187"

st.markdown("""
<style>
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    html, body, .stApp {
        background-color: #050505;
        color: #c8c8c8;
    }
    .stApp {
        background: #050505;
        background-attachment: fixed;
        overflow-x: hidden;
    }

    .orb-layer {
        position: fixed;
        inset: 0;
        overflow: hidden;
        pointer-events: none;
        z-index: 0;
    }
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.32;
        will-change: transform;
    }
    .orb-1 {
        width: 520px; height: 520px;
        background: radial-gradient(circle at 30% 30%, #e63946, #7a1a22 70%);
        top: -120px; left: -100px;
        animation: float1 22s ease-in-out infinite;
    }
    .orb-2 {
        width: 460px; height: 460px;
        background: radial-gradient(circle at 40% 40%, #2a9d8f, #14504a 70%);
        top: 20%; right: -140px;
        animation: float2 28s ease-in-out infinite;
    }
    .orb-3 {
        width: 600px; height: 600px;
        background: radial-gradient(circle at 50% 50%, #d4a373, #6b4f38 70%);
        bottom: -180px; left: 25%;
        animation: float3 32s ease-in-out infinite;
    }
    .orb-4 {
        width: 380px; height: 380px;
        background: radial-gradient(circle at 50% 50%, #6a4c93, #2d1e46 70%);
        bottom: 10%; right: 15%;
        animation: float4 26s ease-in-out infinite;
    }
    .orb-5 {
        width: 300px; height: 300px;
        background: radial-gradient(circle at 50% 50%, #457b9d, #1d3a4c 70%);
        top: 45%; left: 40%;
        animation: float2 30s ease-in-out infinite reverse;
    }
    @keyframes float1 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(80px, 60px) scale(1.15); }
    }
    @keyframes float2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(-70px, 90px) scale(1.1); }
    }
    @keyframes float3 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(60px, -80px) scale(1.2); }
    }
    @keyframes float4 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(-90px, -50px) scale(1.08); }
    }

    .stApp::after {
        content: '';
        position: fixed;
        inset: 0;
        background: radial-gradient(ellipse at center, transparent 20%, rgba(0,0,0,0.85) 100%);
        pointer-events: none;
        z-index: 0;
    }

    section[data-testid="stSidebar"] {
        background: rgba(8, 8, 8, 0.75) !important;
        backdrop-filter: blur(30px) saturate(120%);
        -webkit-backdrop-filter: blur(30px) saturate(120%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div { color: #c8c8c8 !important; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1400px;
        position: relative;
        z-index: 2;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, rgba(22, 22, 24, 0.60) 0%, rgba(14, 14, 16, 0.55) 100%) !important;
        backdrop-filter: blur(45px) saturate(130%);
        -webkit-backdrop-filter: blur(45px) saturate(130%);
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow:
            0 1px 0 rgba(255, 255, 255, 0.04) inset,
            0 20px 60px rgba(0, 0, 0, 0.6) !important;
        padding: 22px 24px !important;
        position: relative;
        overflow: hidden;
        z-index: 2;
    }
    [data-testid="stVerticalBlockBorderWrapper"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 20%;
        right: 20%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
        pointer-events: none;
    }

    .section-label {
        font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 500;
        color: rgba(200, 200, 200, 0.45) !important;
        padding-bottom: 14px;
        margin-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-label::before {
        content: '';
        width: 5px;
        height: 5px;
        background: rgba(220, 220, 220, 0.85);
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.4);
    }

    .stButton > button {
        width: 100%;
        background: rgba(230, 230, 230, 0.92);
        color: #1a1a1a !important;
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        padding: 11px 22px;
        font-weight: 600;
        font-size: 0.86rem;
        letter-spacing: 0.3px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        background: #ffffff;
        border-color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.18);
    }
    .stButton > button:active { transform: translateY(0); }
    .stButton > button p, .stButton > button span { color: #1a1a1a !important; }

    .stTextInput input {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 10px !important;
        color: #c8c8c8 !important;
        font-size: 0.88rem;
        padding: 10px 14px !important;
        transition: all 0.2s ease;
    }
    .stTextInput input:focus {
        border-color: rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.04) !important;
    }
    .stTextInput input::placeholder { color: rgba(200, 200, 200, 0.3) !important; }

    .stSelectbox label, .stRadio label {
        font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
        font-size: 0.62rem !important;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        color: rgba(200, 200, 200, 0.45) !important;
        margin-bottom: 4px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 10px !important;
        color: #c8c8c8 !important;
        min-height: 38px !important;
        font-size: 0.86rem;
        transition: all 0.2s ease;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: rgba(255, 255, 255, 0.18) !important;
        background: rgba(255, 255, 255, 0.055) !important;
    }
    div[data-baseweb="popover"] div[role="listbox"] {
        background: #0e0e0e !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-baseweb="popover"] li { font-size: 0.86rem !important; }
    div[data-baseweb="popover"] li:hover { background: rgba(255, 255, 255, 0.06) !important; }

    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        min-height: auto !important;
        transition: all 0.2s ease;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(255, 255, 255, 0.25) !important;
        background: rgba(255, 255, 255, 0.035) !important;
    }
    section[data-testid="stFileUploaderDropzone"] svg { fill: rgba(200,200,200,0.55) !important; }
    section[data-testid="stFileUploaderDropzone"] button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.13) !important;
        border-radius: 8px !important;
        color: #c8c8c8 !important;
        padding: 5px 14px !important;
        font-size: 0.8rem !important;
    }
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: rgba(255, 255, 255, 0.10) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }

    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    .copyable,
    .result-wrap {
        background: transparent;
        border: none;
        border-left: 1px solid rgba(200, 200, 200, 0.20);
        border-radius: 0;
        padding: 2px 4px 2px 16px;
        margin-top: 18px;
        margin-bottom: 32px;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 0.88rem;
        line-height: 1.65;
        white-space: pre-wrap;
        word-break: break-word;
        color: #b8b8b8;
        overflow: hidden;
    }
    .copyable .hl {
        color: #e8e8e8;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.07);
        padding: 1px 6px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.84rem;
    }

    .copy-icon {
        float: right;
        margin: 0 0 4px 10px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.11);
        color: rgba(200, 200, 200, 0.7);
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
    .copy-icon:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: rgba(255, 255, 255, 0.22);
        color: #e0e0e0;
    }
    .copy-icon:active { transform: scale(0.92); }

    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        color: rgba(200, 200, 200, 0.35) !important;
        letter-spacing: 0.5px;
    }

    .stSpinner > div {
        border-color: rgba(255, 255, 255, 0.12) !important;
        border-top-color: #c8c8c8 !important;
    }

    .stAlert {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #c8c8c8 !important;
    }
</style>

<div class="orb-layer">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="orb orb-4"></div>
    <div class="orb orb-5"></div>
</div>
""", unsafe_allow_html=True)

cookie_manager = stx.CookieManager(key="ck")

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

cookies = cookie_manager.get_all()
if cookies and not st.session_state["gemini_api_key"]:
    saved = cookies.get("gemini_api_key")
    if saved:
        st.session_state["gemini_api_key"] = saved
        st.rerun()


def _persist_key():
    if st.session_state["gemini_api_key"]:
        cookie_manager.set(
            "gemini_api_key",
            st.session_state["gemini_api_key"],
            expires_at=datetime.now() + timedelta(days=365)
        )


IMAGE_ENGINES = [
    "Leonardo.ai",
    "Pollinations",
    "HuggingFace Space",
]

with st.sidebar:
    st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your key…",
        key="gemini_api_key",
        on_change=_persist_key,
        help="Saved in your browser. Enter once — stays forever."
    )
    st.caption(f"model // {MODEL_NAME}")

    st.markdown("---")

    st.radio(
        "Image Engine",
        IMAGE_ENGINES,
        key="image_engine",
        index=0
    )

    if st.session_state.get("image_engine") == "Leonardo.ai":
        st.text_input(
            "Leonardo API Key",
            type="password",
            value=LEONARDO_DEFAULT_TOKEN,
            key="leonardo_key"
        )
    elif st.session_state.get("image_engine") == "HuggingFace Space":
        st.text_input(
            "HF Space name",
            value="multimodalart/qwen-image-edit",
            key="hf_space",
            help="e.g. multimodalart/qwen-image-edit"
        )

    st.caption("rotate your Leonardo key after testing!")

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

MATERIALS = ["wool", "silk", "suede", "leather"]
ITEM_TYPES = ["blazer", "dress", "coat", "top", "skirt"]
MANNEQUIN_PARTS = ["torso", "-"]
BOTTOM_COLORS = ["black", "white", "beige", "grey"]

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
- If a field (Brand, Size, Material, Condition) has NO information on the screenshot, OMIT that entire line completely. Never write "—", "-", "N/A" or any placeholder.
- Everything must be in English.
"""


def copyable_block(html_content: str, block_id: str) -> str:
    return (
        f'<div class="copyable" id="{block_id}">'
        f'<button class="copy-icon" title="Copy" '
        f'onclick="copyBlock(\'{block_id}\', this)">⧉</button>'
        f'{html_content}'
        f'</div>'
    )


def generate_description(prompt: str, image: Image.Image, api_key: str):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def pil_to_jpeg_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def leonardo_upload_init(image: Image.Image, token: str):
    try:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        r = requests.post(
            f"{LEONARDO_API}/init-image",
            headers=headers,
            json={"extension": "jpg"},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()["uploadInitImage"]
        init_id = data["id"]
        upload_url = data["url"]
        fields = json.loads(data["fields"])

        files = {"file": ("image.jpg", pil_to_jpeg_bytes(image), "image/jpeg")}
        r2 = requests.post(upload_url, data=fields, files=files, timeout=60)
        r2.raise_for_status()
        return init_id
    except Exception as e:
        st.error(f"Leonardo upload failed: {e}")
        return None


def generate_leonardo(prompt: str, ref: Image.Image | None, token: str):
    try:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }

        payload = {
            "prompt": prompt,
            "modelId": LEONARDO_MODEL,
            "width": 768,
            "height": 1024,
            "num_images": 1,
            "guidance_scale": 7,
            "public": False,
        }

        if ref is not None:
            init_id = leonardo_upload_init(ref, token)
            if not init_id:
                return None
            payload["init_image_id"] = init_id
            payload["init_strength"] = 0.35
            payload["image_prompt_type"] = "Image"

        r = requests.post(
            f"{LEONARDO_API}/generations",
            headers=headers,
            json=payload,
            timeout=30
        )
        if r.status_code != 200:
            st.error(f"Leonardo API {r.status_code}: {r.text[:300]}")
            return None
        gen_id = r.json()["sdGenerationJob"]["generationId"]

        for _ in range(60):
            time.sleep(2)
            r2 = requests.get(
                f"{LEONARDO_API}/generations/{gen_id}",
                headers=headers,
                timeout=30
            )
            if r2.status_code != 200:
                continue
            job = r2.json().get("generations_by_pk") or {}
            status = job.get("status")
            if status == "COMPLETE":
                imgs = job.get("generated_images", [])
                if imgs:
                    url = imgs[0]["url"]
                    resp = requests.get(url, timeout=60)
                    resp.raise_for_status()
                    return Image.open(io.BytesIO(resp.content))
                return None
            if status == "FAILED":
                st.error("Leonardo generation failed.")
                return None

        st.error("Leonardo timeout.")
        return None
    except Exception as e:
        st.error(f"Leonardo error: {e}")
        return None


def generate_pollinations(prompt: str, ref: Image.Image | None = None):
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=768&height=1024&nologo=true&model=flux"
        )
        r = requests.get(url, timeout=90)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content))
    except Exception as e:
        st.error(f"Pollinations error: {e}")
        return None


def generate_hf_space(prompt: str, ref: Image.Image, space_name: str):
    try:
        from gradio_client import Client, handle_file
        tmp_in = "/tmp/prompties_in.png"
        ref.convert("RGB").save(tmp_in)

        client = Client(space_name)
        result = client.predict(
            image=handle_file(tmp_in),
            prompt=prompt,
            api_name="/inference"
        )
        if isinstance(result, str) and os.path.exists(result):
            return Image.open(result)
        if isinstance(result, (list, tuple)) and result:
            p = result[0]
            if isinstance(p, str) and os.path.exists(p):
                return Image.open(p)
        st.error("Unexpected HF Space response.")
        return None
    except Exception as e:
        st.error(f"HF Space error: {e}")
        return None


def generate_image(prompt: str, ref: Image.Image | None):
    engine = st.session_state.get("image_engine", "Leonardo.ai")
    if engine == "Leonardo.ai":
        token = st.session_state.get("leonardo_key", "").strip()
        if not token:
            st.error("Leonardo API key missing.")
            return None
        return generate_leonardo(prompt, ref, token)
    if engine == "Pollinations":
        return generate_pollinations(prompt, ref)
    if engine == "HuggingFace Space":
        space = st.session_state.get("hf_space", "").strip()
        if not space:
            st.error("HF Space name missing.")
            return None
        if ref is None:
            st.error("HF Space requires a reference image.")
            return None
        return generate_hf_space(prompt, ref, space)
    return None


st.markdown(COPY_JS, unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")

with left:
    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Generate Description</div>',
            unsafe_allow_html=True
        )

        uploaded = st.file_uploader(
            "Screenshot",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )

        screenshot = None
        if uploaded:
            try:
                screenshot = Image.open(uploaded)
                st.image(screenshot, width=120)
            except Exception as e:
                st.error(f"Cannot open image: {e}")

        if st.button("Generate Description", use_container_width=True):
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
                f'<div class="result-wrap" id="result-block">'
                f'<button class="copy-icon" title="Copy" '
                f'onclick="copyBlock(\'result-block\', this)">⧉</button>'
                f'{safe}</div>',
                unsafe_allow_html=True
            )

with right:
    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Prompt / Mannequin</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        material1 = c1.selectbox("Material", MATERIALS, key="p1_mat")
        item1 = c2.selectbox("Item", ITEM_TYPES, key="p1_item")
        part1 = c3.selectbox("Mannequin", MANNEQUIN_PARTS, key="p1_part")

        p1 = (
            f'Generate a high-resolution studio photo of this '
            f'<span class="hl">{material1}</span> '
            f'<span class="hl">{item1}</span>, '
            f'preserving every detail, on a headless/armless feminine cream linen mannequin '
            f'<span class="hl">{part1}</span>, '
            f'turned three-quarters toward the left side of the frame with soft incoming light, '
            f'against a plain dark background'
        )
        st.markdown(copyable_block(p1, "prompt1"), unsafe_allow_html=True)

        p1_plain = (
            f"Generate a high-resolution studio photo of this {material1} {item1}, "
            f"preserving every detail, on a headless/armless feminine cream linen mannequin "
            f"{part1}, turned three-quarters toward the left side of the frame with soft "
            f"incoming light, against a plain dark background"
        )

        if st.button("Generate Mannequin Photo", use_container_width=True, key="gen_p1"):
            ref = screenshot
            with st.spinner(f"Generating with {st.session_state.get('image_engine')}…"):
                img = generate_image(p1_plain, ref)
                if img:
                    st.session_state["img_p1"] = img

        if st.session_state.get("img_p1") is not None:
            st.image(st.session_state["img_p1"], use_container_width=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Prompt / Model</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        material2 = c1.selectbox("Material", MATERIALS, key="p2_mat")
        item2 = c2.selectbox("Item", ITEM_TYPES, key="p2_item")
        bottom = c3.selectbox("Trousers", BOTTOM_COLORS, key="p2_bottom")

        p2 = (
            f'Fashion e-commerce photography, mid-shot of a model, wearing this '
            f'<span class="hl">{material2}</span> '
            f'<span class="hl">{item2}</span> and '
            f'<span class="hl">{bottom}</span> high-waist wide-leg trousers. '
            f'Faceless framing, cropped at the chin, casual pose. '
            f'Clean light neutral grey studio background. Soft diffused lighting, minimalist aesthetic, '
            f'effortless chic, high contrast, sharp clothing details, photorealistic '
            f'--ar 3:4 --style raw'
        )
        st.markdown(copyable_block(p2, "prompt2"), unsafe_allow_html=True)

        p2_plain = (
            f"Fashion e-commerce photography, mid-shot of a model, wearing this "
            f"{material2} {item2} and {bottom} high-waist wide-leg trousers. "
            f"Faceless framing, cropped at the chin, casual pose. "
            f"Clean light neutral grey studio background. Soft diffused lighting, "
            f"minimalist aesthetic, effortless chic, high contrast, sharp clothing "
            f"details, photorealistic"
        )

        if st.button("Generate Model Photo", use_container_width=True, key="gen_p2"):
            ref = screenshot
            with st.spinner(f"Generating with {st.session_state.get('image_engine')}…"):
                img = generate_image(p2_plain, ref)
                if img:
                    st.session_state["img_p2"] = img

        if st.session_state.get("img_p2") is not None:
            st.image(st.session_state["img_p2"], use_container_width=True)