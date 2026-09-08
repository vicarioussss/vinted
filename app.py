import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- Настройка страницы ----------
st.set_page_config(
    page_title="Fashion Card Generator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Стили (современный UI) ----------
st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: 700; color: #1E1E1E; margin-bottom: 1rem; }
        .sub-header { font-size: 1.5rem; font-weight: 600; color: #333; }
        .generated-image { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .stButton button { width: 100%; border-radius: 8px; font-weight: 500; }
        .stCodeBlock { border-radius: 8px; }
        .info-box { background-color: #f0f2f6; padding: 1rem; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ---------- Боковая панель ----------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/clothes.png", width=80)
    st.title("Настройки")

    api_key = st.text_input(
        "🔑 Google Gemini API Key",
        type="password",
        placeholder="Введите ваш API-ключ...",
        help="Получите ключ в Google AI Studio"
    )

    model_options = [
        "gemini-2.0-flash-exp-image-generation",  # для генерации изображений
        "gemini-2.0-flash",                       # для текста
        "gemini-1.5-pro",                         # для текста
    ]
    selected_model = st.selectbox(
        "🤖 Модель Gemini",
        options=model_options,
        index=0,
        help="Для генерации изображений используйте модель с 'image-generation'"
    )

    with st.expander("ℹ️ Справка"):
        st.markdown("""
            **Как работать с приложением:**

            1. **Вкладка «Генерация изображений»**  
               - Загрузите фото вещи (референс).  
               - Настройте параметры для двух промптов (манекен и модель).  
               - Нажмите «Сгенерировать фото» – получите два варианта.

            2. **Вкладка «Генерация описания»**  
               - Загрузите скриншот с данными о вещи (состав, мерки и т.д.).  
               - Нажмите «Сгенерировать описание» – получите готовый текст для карточки товара.

            **Важно:**  
            - Для генерации изображений необходима модель `gemini-2.0-flash-exp-image-generation`.  
            - Для описания можно использовать любую из выбранных моделей (текстовых).
        """)

# ---------- Инициализация сессии ----------
if "generated_images" not in st.session_state:
    st.session_state.generated_images = {}
if "description_text" not in st.session_state:
    st.session_state.description_text = ""

# ---------- Функции для API ----------
def init_genai(api_key: str):
    """Инициализация клиента Gemini."""
    genai.configure(api_key=api_key)

def generate_image(prompt: str, reference_image: Image.Image, model_name: str, api_key: str):
    """Генерация изображения через модель Gemini (с поддержкой image-generation)."""
    try:
        init_genai(api_key)
        model = genai.GenerativeModel(model_name)
        # Передаём промпт и референс
        response = model.generate_content(
            [prompt, reference_image],
            generation_config=genai.types.GenerationConfig(
                response_modalities=["IMAGE"]
            )
        )
        # Извлекаем изображение из ответа
        for part in response.parts:
            if part.inline_data is not None and part.inline_data.mime_type.startswith("image/"):
                image_data = part.inline_data.data
                return Image.open(io.BytesIO(image_data))
        return None
    except Exception as e:
        st.error(f"Ошибка генерации изображения: {str(e)}")
        return None

def generate_description(prompt: str, screenshot: Image.Image, model_name: str, api_key: str):
    """Генерация текстового описания через текстовую модель Gemini."""
    try:
        init_genai(api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"Ошибка генерации описания: {str(e)}")
        return None

# ---------- Вкладки ----------
tab1, tab2 = st.tabs(["🖼️ Генерация изображений (Манекен & Модель)", "📝 Генерация описания (по скриншоту)"])

# ================== ВКЛАДКА 1 ==================
with tab1:
    st.markdown('<div class="main-header">Генерация изображений</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Загрузка референса
        uploaded_ref = st.file_uploader(
            "📤 Загрузите фотографию вещи (референс)",
            type=["jpg", "jpeg", "png"],
            help="Фото вещи на манекене или просто отдельно"
        )
        if uploaded_ref:
            ref_image = Image.open(uploaded_ref)
            st.image(ref_image, caption="Исходное фото", use_column_width=True)
        else:
            ref_image = None

    with col_right:
        st.markdown('<div class="sub-header">Настройки промптов</div>', unsafe_allow_html=True)

        # Промпт №1 (Манекен)
        with st.expander("🧍 Промпт №1 – Стильный манекен", expanded=True):
            material1 = st.selectbox(
                "Материал",
                options=["leather", "wool", "cotton", "silk", "polyester", "denim"],
                index=0,
                key="mat1"
            )
            item_type1 = st.selectbox(
                "Тип вещи",
                options=["blazer", "jacket", "coat", "dress", "skirt", "trousers", "shirt"],
                index=0,
                key="type1"
            )
            mannequin_part = st.selectbox(
                "Часть манекена",
                options=["torso", "full body"],
                index=0
            )

        # Промпт №2 (Модель)
        with st.expander("👩 Промпт №2 – Модель", expanded=False):
            material2 = st.selectbox(
                "Материал",
                options=["wool", "leather", "cotton", "silk", "polyester", "denim"],
                index=0,
                key="mat2"
            )
            item_type2 = st.selectbox(
                "Тип вещи",
                options=["blazer", "jacket", "coat", "dress", "skirt", "trousers", "shirt"],
                index=0,
                key="type2"
            )
            bottom_color = st.text_input("Цвет низа", value="black")
            bottom_type = st.text_input("Тип низа/брюк", value="high-waist wide-leg trousers")

        # Кнопка генерации
        if st.button("🚀 Сгенерировать фото", use_container_width=True):
            if not api_key:
                st.error("❌ Введите API-ключ в боковой панели.")
            elif not uploaded_ref:
                st.error("❌ Загрузите референсное фото.")
            elif not selected_model.startswith("gemini-2.0-flash-exp-image-generation"):
                st.warning("⚠️ Для генерации изображений рекомендуется использовать модель 'gemini-2.0-flash-exp-image-generation'.")
            else:
                # Формируем промпты
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

                # Прогресс-бар
                progress_bar = st.progress(0, text="Генерация изображений...")
                status_text = st.empty()

                # Функции для параллельного выполнения
                def gen1():
                    status_text.text("Генерируем фото на манекене...")
                    return generate_image(prompt1, ref_image, selected_model, api_key)

                def gen2():
                    status_text.text("Генерируем фото на модели...")
                    return generate_image(prompt2, ref_image, selected_model, api_key)

                # Запускаем параллельно
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future1 = executor.submit(gen1)
                    future2 = executor.submit(gen2)
                    results = {}
                    for i, future in enumerate(as_completed([future1, future2])):
                        progress_bar.progress((i+1)/2)
                        if future == future1:
                            results["mannequin"] = future.result()
                        else:
                            results["model"] = future.result()

                progress_bar.empty()
                status_text.empty()

                # Сохраняем в сессию для отображения
                st.session_state.generated_images = results

    # Отображение результатов в двух колонках
    if "mannequin" in st.session_state.generated_images:
        img1 = st.session_state.generated_images.get("mannequin")
        img2 = st.session_state.generated_images.get("model")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧍 Манекен")
            if img1:
                st.image(img1, use_column_width=True)
                # Кнопка скачивания
                buf = io.BytesIO()
                img1.save(buf, format="PNG")
                st.download_button(
                    label="📥 Скачать",
                    data=buf.getvalue(),
                    file_name="mannequin.png",
                    mime="image/png"
                )
            else:
                st.info("Не удалось сгенерировать изображение.")
        with col2:
            st.subheader("👩 Модель")
            if img2:
                st.image(img2, use_column_width=True)
                buf = io.BytesIO()
                img2.save(buf, format="PNG")
                st.download_button(
                    label="📥 Скачать",
                    data=buf.getvalue(),
                    file_name="model.png",
                    mime="image/png"
                )
            else:
                st.info("Не удалось сгенерировать изображение.")

# ================== ВКЛАДКА 2 ==================
with tab2:
    st.markdown('<div class="main-header">Генерация описания</div>', unsafe_allow_html=True)

    # Загрузка скриншота
    uploaded_screenshot = st.file_uploader(
        "📸 Загрузите скриншот с данными о вещи (состав, мерки, бренд)",
        type=["jpg", "jpeg", "png"],
        help="Скриншот страницы товара (например, с Sellpy)"
    )

    if uploaded_screenshot:
        screenshot = Image.open(uploaded_screenshot)
        st.image(screenshot, caption="Загруженный скриншот", use_column_width=True)
    else:
        screenshot = None

    # Промпт для описания (можно сделать редактируемым, но оставим фиксированным)
    description_prompt = (
        "Проанализируй данный скриншот с информацией о вещи. "
        "Извлеки все ключевые данные (бренд, состав, замеры, состояние, особенности) "
        "и составь привлекательное, структурированное и продающее описание товара "
        "для онлайн-магазина одежды в Instagram/на сайте. "
        "Используй эмодзи, списки и четкие блоки (Описание, Состав, Замеры, Стиль)."
    )

    if st.button("✨ Сгенерировать описание", use_container_width=True):
        if not api_key:
            st.error("❌ Введите API-ключ в боковой панели.")
        elif not uploaded_screenshot:
            st.error("❌ Загрузите скриншот.")
        else:
            with st.spinner("Генерируем описание..."):
                description = generate_description(
                    description_prompt,
                    screenshot,
                    selected_model,
                    api_key
                )
                if description:
                    st.session_state.description_text = description
                else:
                    st.session_state.description_text = ""

    # Отображение результата
    if st.session_state.description_text:
        st.markdown("### 📝 Готовое описание")
        # Используем st.code с кнопкой копирования (по умолчанию есть)
        st.code(st.session_state.description_text, language="markdown", wrap_lines=True)
        # Дополнительно кнопка скачивания
        st.download_button(
            label="📥 Скачать описание (TXT)",
            data=st.session_state.description_text,
            file_name="description.txt",
            mime="text/plain"
        )