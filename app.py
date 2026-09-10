import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import urllib.parse
import requests

st.set_page_config(page_title="Fashion Generator", page_icon="👗", layout="wide")
st.title("👗 Генерация карточек товаров")

# ---------- Боковая панель ----------
with st.sidebar:
    st.header("Настройки")
    api_key = st.text_input("🔑 Google Gemini API Key", type="password",
                            help="Нужен для вкладки «Описание». Для картинок можно использовать Pollinations (бесплатно).")

    st.subheader("🖼️ Генератор изображений")
    image_backend = st.radio(
        "Движок",
        options=["Pollinations (бесплатно, без ключа)", "Gemini (нужен биллинг)"],
        index=0,
        help="Pollinations работает без API-ключа и бесплатно. Gemini требует включённого биллинга Google Cloud."
    )

    if image_backend.startswith("Gemini"):
        img_model_name = st.selectbox(
            "Модель Gemini для изображений",
            options=[
                "models/gemini-2.5-flash-image",
                "models/gemini-3.1-flash-image",
                "models/gemini-3-pro-image",
            ],
            index=0
        )
    else:
        img_model_name = None
        st.caption("Pollinations не требует ключа и работает без ограничений.")

    st.markdown("---")
    st.subheader("📝 Модель для описания")
    text_model = st.selectbox(
        "Gemini для текста",
        options=["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-pro"],
        index=0
    )

# ---------- Утилиты ----------
def generate_image_pollinations(prompt: str, width=768, height=1024) -> Image.Image | None:
    """Генерация изображения через бесплатный Pollinations.ai"""
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&model=flux"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content))
    except Exception as e:
        st.error(f"Ошибка Pollinations: {e}")
        return None

def generate_image_gemini(prompt, ref_image, model_name, api_key):
    """Генерация изображения через Gemini (нужен биллинг)."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        content = [prompt, ref_image] if ref_image else prompt
        try:
            response = model.generate_content(
                content,
                generation_config=genai.types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
        except (AttributeError, TypeError):
            response = model.generate_content(
                content,
                generation_config={"response_modalities": ["IMAGE"]}
            )
        for part in response.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                return Image.open(io.BytesIO(part.inline_data.data))
        st.warning("Gemini не вернул изображение. Возможно, квота исчерпана или контент заблокирован.")
        return None
    except Exception as e:
        err = str(e)
        if "429" in err or "Quota exceeded" in err:
            st.error("❌ Превышена квота Gemini (429). Включите биллинг или используйте Pollinations.")
        else:
            st.error(f"Ошибка Gemini: {e}")
        return None

def generate_description(prompt, screenshot, model_name, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"Ошибка генерации описания: {e}")
        return None

# ---------- Вкладки ----------
tab1, tab2 = st.tabs(["🖼️ Генерация изображений", "📝 Генерация описания"])

# ============ ВКЛАДКА 1 ============
with tab1:
    st.header("Генерация изображений")

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("📤 Загрузите фото вещи (референс)", type=["jpg", "jpeg", "png"])
        ref_image = None
        if uploaded_file:
            try:
                ref_image = Image.open(uploaded_file)
                st.image(ref_image, caption="Референс", use_container_width=True)
            except Exception as e:
                st.error(f"Ошибка загрузки: {e}")

    with col2:
        material = st.selectbox("Материал", ["leather", "wool", "cotton", "silk", "polyester", "denim"], index=0)
        item_type = st.selectbox("Тип вещи", ["blazer", "jacket", "coat", "dress", "skirt", "trousers", "shirt"], index=0)
        mannequin_part = st.selectbox("Часть манекена", ["torso", "full body"], index=0)

        if st.button("🚀 Сгенерировать фото", use_container_width=True):
            prompt_mannequin = (
                f"Studio photo of a {material} {item_type} on a headless mannequin {mannequin_part}, "
                f"plain dark background, soft studio lighting, photorealistic, high detail"
            )
            prompt_model = (
                f"Fashion e-commerce photo, mid-shot of a model wearing a {material} {item_type} "
                f"and black high-waist wide-leg trousers, faceless framing, clean light grey background, "
                f"soft diffused light, minimalist, photorealistic"
            )

            if image_backend.startswith("Pollinations"):
                with st.spinner("Генерация через Pollinations..."):
                    img1 = generate_image_pollinations(prompt_mannequin, 768, 1024)
                    img2 = generate_image_pollinations(prompt_model, 768, 1024)
            else:
                if not api_key:
                    st.error("Введите API-ключ или переключитесь на Pollinations.")
                    img1 = img2 = None
                else:
                    with st.spinner("Генерация через Gemini..."):
                        img1 = generate_image_gemini(prompt_mannequin, ref_image, img_model_name, api_key)
                        img2 = generate_image_gemini(prompt_model, ref_image, img_model_name, api_key)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🧍 Манекен")
                if img1:
                    st.image(img1, use_container_width=True)
                    buf = io.BytesIO(); img1.save(buf, "PNG")
                    st.download_button("📥 Скачать", buf.getvalue(), "mannequin.png", "image/png")
                else:
                    st.info("Не удалось сгенерировать.")
            with c2:
                st.subheader("👩 Модель")
                if img2:
                    st.image(img2, use_container_width=True)
                    buf = io.BytesIO(); img2.save(buf, "PNG")
                    st.download_button("📥 Скачать", buf.getvalue(), "model.png", "image/png")
                else:
                    st.info("Не удалось сгенерировать.")

# ============ ВКЛАДКА 2 ============
with tab2:
    st.header("Генерация описания")

    uploaded_screenshot = st.file_uploader("📸 Загрузите скриншот с данными о вещи", type=["jpg", "jpeg", "png"])
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
            st.error("❌ Введите Gemini API-ключ.")
        elif not screenshot:
            st.error("❌ Загрузите скриншот.")
        else:
            with st.spinner("Генерируем описание..."):
                desc = generate_description(description_prompt, screenshot, text_model, api_key)
                if desc:
                    st.session_state["description_text"] = desc

    if st.session_state.get("description_text"):
        st.markdown("### 📝 Готовое описание")
        st.code(st.session_state["description_text"], language="markdown", wrap_lines=True)
        st.download_button(
            "📥 Скачать описание (TXT)",
            st.session_state["description_text"],
            "description.txt",
            "text/plain"
        )