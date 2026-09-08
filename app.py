import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(
    page_title="Fashion Card Generator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: 700; color: #1E1E1E; margin-bottom: 1rem; }
        .sub-header { font-size: 1.5rem; font-weight: 600; color: #333; }
        .stButton button { width: 100%; border-radius: 8px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/clothes.png", width=80)
    st.title("Настройки")
    api_key = st.text_input(
        "🔑 Google Gemini API Key",
        type="password",
        placeholder="Введите ваш API-ключ...",
        help="Получите ключ в Google AI Studio"
    )
    img_model = st.selectbox(
        "🖼️ Модель для генерации изображений",
        options=["gemini-2.0-flash-exp-image-generation"],
        index=0,
        help="Только эта модель поддерживает создание картинок"
    )
    text_model = st.selectbox(
        "📝 Модель для описания",
        options=["gemini-2.0-flash", "gemini-1.5-pro"],
        index=0,
        help="Используется для анализа скриншота и генерации текста"
    )
    with st.expander("ℹ️ Справка"):
        st.markdown("""
            **Как работать:**

            1. **Вкладка «Генерация изображений»**  
               - Загрузите фото вещи.  
               - Настройте параметры промптов.  
               - Нажмите «Сгенерировать фото» – получите два варианта.

            2. **Вкладка «Генерация описания»**  
               - Загрузите скриншот с данными о вещи.  
               - Нажмите «Сгенерировать описание» – получите структурированный текст.
        """)

if "generated_images" not in st.session_state:
    st.session_state.generated_images = {}
if "description_text" not in st.session_state:
    st.session_state.description_text = ""

def init_genai(api_key: str):
    genai.configure(api_key=api_key)

def generate_image(prompt: str, reference_image: Image.Image, model_name: str, api_key: str):
    try:
        init_genai(api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            [prompt, reference_image],
            generation_config=genai.types.GenerationConfig(
                response_modalities=["IMAGE"]
            )
        )
        for part in response.parts:
            if part.inline_data is not None and part.inline_data.mime_type.startswith("image/"):
                return Image.open(io.BytesIO(part.inline_data.data))
        return None
    except Exception as e:
        st.error(f"Ошибка генерации изображения: {str(e)}")
        return None

def generate_description(prompt: str, screenshot: Image.Image, model_name: str, api_key: str):
    try:
        init_genai(api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"Ошибка генерации описания: {str(e)}")
        return None

tab1, tab2 = st.tabs(["🖼️ Генерация изображений", "📝 Генерация описания"])

with tab1:
    st.markdown('<div class="main-header">Генерация изображений</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1])
    with col_left:
        uploaded_ref = st.file_uploader(
            "📤 Загрузите фотографию вещи (референс)",
            type=["jpg", "jpeg", "png"]
        )
        ref_image = None
        if uploaded_ref:
            try:
                ref_image = Image.open(uploaded_ref)
                st.image(ref_image, caption="Исходное фото", use_container_width=True)
            except Exception as e:
                st.error(f"Не удалось загрузить изображение: {e}")
    with col_right:
        st.markdown('<div class="sub-header">Настройки промптов</div>', unsafe_allow_html=True)
        with st.expander("🧍 Промпт №1 – Манекен", expanded=True):
            material1 = st.selectbox("Материал", ["leather", "wool", "cotton", "silk", "polyester", "denim"], index=0, key="mat1")
            item_type1 = st.selectbox("Тип вещи", ["blazer", "jacket", "coat", "dress", "skirt", "trousers", "shirt"], index=0, key="type1")
            mannequin_part = st.selectbox("Часть манекена", ["torso", "full body"], index=0)
        with st.expander("👩 Промпт №2 – Модель", expanded=False):
            material2 = st.selectbox("Материал", ["wool", "leather", "cotton", "silk", "polyester", "denim"], index=0, key="mat2")
            item_type2 = st.selectbox("Тип вещи", ["blazer", "jacket", "coat", "dress", "skirt", "trousers", "shirt"], index=0, key="type2")
            bottom_color = st.text_input("Цвет низа", value="black")
            bottom_type = st.text_input("Тип низа/брюк", value="high-waist wide-leg trousers")

        if st.button("🚀 Сгенерировать фото", use_container_width=True):
            if not api_key:
                st.error("❌ Введите API-ключ.")
            elif not uploaded_ref or ref_image is None:
                st.error("❌ Загрузите корректное референсное фото.")
            else:
                prompt1 = (
                    f"Generate a high-resolution studio photo of this {material1} {item_type1}, "
                    f"preserving every detail, on a headless/armless feminine cream linen mannequin {mannequin_part}, "
                    f"turned three-quarters toward the left side of the frame with soft incoming light, "
                    f"against a plain dark background"
                )
                prompt2 = (
                    f"Fashion e-commerce photography, mid-shot of a model, wearing a {material2} {item_type2} "
                    f"and {bottom_color} {bottom_type}. Faceless framing, cropped at the chin, casual pose "
                    f"with one hand in pocket. Clean light neutral grey studio background. Soft diffused lighting, "
                    f"minimalist aesthetic, effortless chic, high contrast, sharp clothing details, photorealistic "
                    f"--ar 3:4 --style raw"
                )

                progress_bar = st.progress(0, text="Генерация изображений...")

                def gen1():
                    return generate_image(prompt1, ref_image, img_model, api_key)
                def gen2():
                    return generate_image(prompt2, ref_image, img_model, api_key)

                results = {}
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future1 = executor.submit(gen1)
                    future2 = executor.submit(gen2)
                    for i, future in enumerate(as_completed([future1, future2])):
                        progress_bar.progress((i+1)/2)
                        if future == future1:
                            results["mannequin"] = future.result()
                        else:
                            results["model"] = future.result()

                progress_bar.empty()
                st.session_state.generated_images = results

    if "mannequin" in st.session_state.generated_images:
        img1, img2 = st.session_state.generated_images.get("mannequin"), st.session_state.generated_images.get("model")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧍 Манекен")
            if img1:
                st.image(img1, use_container_width=True)
                buf = io.BytesIO()
                img1.save(buf, format="PNG")
                st.download_button("📥 Скачать", data=buf.getvalue(), file_name="mannequin.png", mime="image/png")
            else:
                st.info("Не удалось сгенерировать.")
        with col2:
            st.subheader("👩 Модель")
            if img2:
                st.image(img2, use_container_width=True)
                buf = io.BytesIO()
                img2.save(buf, format="PNG")
                st.download_button("📥 Скачать", data=buf.getvalue(), file_name="model.png", mime="image/png")
            else:
                st.info("Не удалось сгенерировать.")

with tab2:
    st.markdown('<div class="main-header">Генерация описания</div>', unsafe_allow_html=True)
    uploaded_screenshot = st.file_uploader(
        "📸 Загрузите скриншот с данными о вещи",
        type=["jpg", "jpeg", "png"]
    )
    screenshot = None
    if uploaded_screenshot:
        try:
            screenshot = Image.open(uploaded_screenshot)
            st.image(screenshot, caption="Скриншот", use_container_width=True)
        except Exception as e:
            st.error(f"Ошибка загрузки: {e}")

    description_prompt = (
        "Проанализируй данный скриншот с информацией о вещи. "
        "Извлеки все ключевые данные (бренд, состав, замеры, состояние, особенности) "
        "и составь привлекательное, структурированное и продающее описание товара "
        "для онлайн-магазина одежды в Instagram/на сайте. "
        "Используй эмодзи, списки и четкие блоки (Описание, Состав, Замеры, Стиль)."
    )

    if st.button("✨ Сгенерировать описание", use_container_width=True):
        if not api_key:
            st.error("❌ Введите API-ключ.")
        elif not uploaded_screenshot or screenshot is None:
            st.error("❌ Загрузите корректный скриншот.")
        else:
            with st.spinner("Генерируем описание..."):
                description = generate_description(description_prompt, screenshot, text_model, api_key)
                if description:
                    st.session_state.description_text = description
                else:
                    st.session_state.description_text = ""

    if st.session_state.description_text:
        st.markdown("### 📝 Готовое описание")
        st.code(st.session_state.description_text, language="markdown", wrap_lines=True)
        st.download_button(
            label="📥 Скачать описание (TXT)",
            data=st.session_state.description_text,
            file_name="description.txt",
            mime="text/plain"
        )