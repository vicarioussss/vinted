import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ==================== КОНФИГ ====================
st.set_page_config(
    page_title="AI Fashion Descriptions",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== GLASSMORPHISM СТИЛЬ ====================
st.markdown("""
<style>
    /* ---------- Фон: градиент + мягкие пятна ---------- */
    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(255, 154, 158, 0.45), transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(161, 196, 253, 0.45), transparent 45%),
            radial-gradient(circle at 50% 85%, rgba(186, 156, 255, 0.40), transparent 45%),
            radial-gradient(circle at 80% 80%, rgba(120, 219, 226, 0.40), transparent 50%),
            linear-gradient(135deg, #1b1b2f 0%, #2a2a44 50%, #1f1f33 100%);
        background-attachment: fixed;
        color: #f2f2f7;
    }

    /* Прячем стандартный фон сайдбара и красим под стекло */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(18px) saturate(160%);
        -webkit-backdrop-filter: blur(18px) saturate(160%);
        border-right: 1px solid rgba(255, 255, 255, 0.15);
    }

    /* Заголовки */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #f2f2f7 !important;
    }

    /* ---------- Стеклянные контейнеры ---------- */
    .glass {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px) saturate(160%);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.20);
        padding: 24px 28px;
        margin-bottom: 20px;
    }

    /* ---------- Кнопки ---------- */
    .stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 14px;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.3px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.22);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.45);
    }
    .stDownloadButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.12);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 14px;
        padding: 10px 20px;
        backdrop-filter: blur(12px);
    }
    .stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.22);
    }

    /* ---------- Поля ввода ---------- */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.20) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        backdrop-filter: blur(12px);
    }

    /* ---------- File uploader ---------- */
    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 2px dashed rgba(255, 255, 255, 0.30) !important;
        border-radius: 18px !important;
        backdrop-filter: blur(14px);
    }

    /* ---------- Вкладки ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 6px;
        border-radius: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #e5e5ee;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.15);
        color: #fff;
    }

    /* ---------- Блок результата ---------- */
    .result-box {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(22px) saturate(160%);
        -webkit-backdrop-filter: blur(22px) saturate(160%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.22);
        padding: 26px 30px;
        margin-top: 16px;
        white-space: pre-wrap;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.98rem;
        line-height: 1.6;
        color: #f5f5fa;
    }

    /* Скрыть верхний декор Streamlit */
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.markdown("### ✨ AI Fashion Studio")
    st.markdown("---")

    api_key = st.text_input(
        "🔑 Google Gemini API Key",
        type="password",
        placeholder="Введите ваш ключ...",
        help="Получить ключ: https://aistudio.google.com/apikey"
    )

    text_model = st.selectbox(
        "📝 Модель Gemini",
        options=["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-2.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Для текстового анализа подойдёт любая из этих моделей."
    )

    st.markdown("---")
    with st.expander("ℹ️ Как пользоваться"):
        st.markdown("""
        1. Вставьте **API-ключ** Google Gemini.  
        2. Загрузите **скриншот** с информацией о вещи  
           (бренд, состав, мерки, состояние).  
        3. Нажмите **«Сгенерировать описание»**.  
        4. Скопируйте или скачайте готовый текст.
        """)

# ==================== ЗАГОЛОВОК ====================
st.markdown("""
<div class="glass" style="text-align:center;">
    <h1 style="margin:0; font-size:2.2rem; letter-spacing:1px;">👗 AI Fashion Description</h1>
    <p style="margin-top:8px; opacity:0.85; font-size:1.05rem;">
        Превратите скриншот с данными о вещи в готовое продающее описание
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== ПРОМПТ ====================
DESCRIPTION_PROMPT = """Ты — профессиональный копирайтер для онлайн-магазина винтажной и брендовой одежды.

Проанализируй скриншот с информацией о вещи и составь карточку товара СТРОГО в таком формате (без каких-либо вводных фраз, без markdown-разметки кроме переносов строк):

НАЗВАНИЕ
Полное название товара: бренд + состав/материал + цвет + ключевая особенность (воротник, крой и т.п.) + тип вещи + размер. Например:
"Peter Nygård 100% Wool Red Mandarin Collar Blazer – Size 38 / M"

ОПИСАНИЕ
Одно ёмкое абзацное описание (3–5 предложений) на английском языке. Опиши материал, крой, детали (воротник, пуговицы, отделка), цвет, стиль и уместность (сезон, повод). Пиши привлекательно и продающе, как для Instagram/сайта.

ДЕТАЛИ
Brand: <бренд>
Size: <размер> (<мерки, если указаны: shoulder width, sleeve length, chest, length>)
Material: <состав, с процентами и оригинальным названием в скобках, если есть>
Condition: <состояние — например, "Good pre-owned condition" или точное описание>

KEYWORDS
Список из 10–15 ключевых слов через запятую в одну строку (lowercase, для SEO и поиска в Instagram). Включи: бренд, материал, цвет, тип одежды, стиль, особенности (collar, piping, buttons и т.п.).

ВАЖНО:
- Если каких-то данных нет на скриншоте — не выдумывай, пропусти или напиши "—".
- Описание и ключевые слова — на английском языке. Название — тоже на английском.
- Никаких вступлений, комментариев и объяснений — только готовая карточка в описанном формате.
"""

# ==================== ФУНКЦИЯ ГЕНЕРАЦИИ ====================
def generate_description(prompt: str, screenshot: Image.Image, model_name: str, api_key: str) -> str | None:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"❌ Ошибка при вызове API: {e}")
        return None

# ==================== ОСНОВНОЙ БЛОК ====================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("#### 📸 Скриншот с данными о вещи")
    uploaded_screenshot = st.file_uploader(
        "Загрузите изображение",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    screenshot = None
    if uploaded_screenshot:
        try:
            screenshot = Image.open(uploaded_screenshot)
            st.image(screenshot, caption="Загруженный скриншот", use_container_width=True)
        except Exception as e:
            st.error(f"Не удалось открыть изображение: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ Управление")

    if st.button("✨ Сгенерировать описание", use_container_width=True):
        if not api_key:
            st.error("❌ Введите API-ключ в боковой панели.")
        elif screenshot is None:
            st.error("❌ Загрузите скриншот с информацией о вещи.")
        else:
            with st.spinner("Генерируем описание..."):
                desc = generate_description(DESCRIPTION_PROMPT, screenshot, text_model, api_key)
                if desc:
                    st.session_state["description_text"] = desc.strip()

    if st.session_state.get("description_text"):
        st.download_button(
            label="📥 Скачать описание (TXT)",
            data=st.session_state["description_text"],
            file_name="description.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.caption("Результат появится ниже после генерации.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== РЕЗУЛЬТАТ ====================
if st.session_state.get("description_text"):
    st.markdown("### 📝 Готовое описание")
    st.markdown(
        f'<div class="result-box">{st.session_state["description_text"]}</div>',
        unsafe_allow_html=True
    )

    # Скрытое поле для быстрого копирования
    with st.expander("📋 Скопировать текст (нажмите, чтобы раскрыть)"):
        st.code(st.session_state["description_text"], language=None)