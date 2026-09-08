import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Fashion Card Generator", page_icon="👗", layout="wide")
st.markdown("""
    <style>.main-header { font-size: 2.5rem; font-weight: 700; } .stButton button { width: 100%; }</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/clothes.png", width=80)
    api_key = st.text_input("🔑 Google Gemini API Key", type="password")
    img_model = "gemini-2.0-flash-exp-image-generation"
    text_model = st.selectbox("📝 Модель для описания", ["gemini-3.6-flash", "gemini-1.5-pro"])

def init_genai(key): genai.configure(api_key=key)

def generate_image(prompt, ref_img, model_name, api_key):
    try:
        init_genai(api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            [prompt, ref_img],
            generation_config=genai.types.GenerationConfig(response_modalities=["IMAGE"])
        )
        st.write("### 📦 Ответ API:")
        st.code(str(response), language="text")
        for part in response.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                return Image.open(io.BytesIO(part.inline_data.data))
        if hasattr(response, 'text') and response.text:
            st.error(f"Текст от модели: {response.text[:500]}")
        else:
            st.warning("Нет изображения и нет текста.")
        return None
    except Exception as e:
        st.error(f"Исключение: {e}")
        return None

def generate_description(prompt, screenshot, model_name, api_key):
    try:
        init_genai(api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, screenshot])
        return response.text
    except Exception as e:
        st.error(f"Ошибка описания: {e}")
        return None

tab1, tab2 = st.tabs(["🖼️ Генерация изображений", "📝 Генерация описания"])

with tab1:
    st.header("Генерация изображений")
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded = st.file_uploader("Загрузите фото", type=["jpg", "png"])
        ref = None
        if uploaded:
            ref = Image.open(uploaded)
            st.image(ref, use_container_width=True)
    with col2:
        material = st.selectbox("Материал", ["leather", "wool", "cotton"], index=0)
        item = st.selectbox("Тип вещи", ["blazer", "jacket", "dress"], index=0)
        part = st.selectbox("Манекен", ["torso", "full body"])
        if st.button("Сгенерировать"):
            if not api_key: st.error("Введите ключ")
            elif not ref: st.error("Загрузите фото")
            else:
                p1 = f"Generate studio photo of {material} {item} on mannequin {part}, dark background"
                p2 = f"Model wearing {material} {item} and black trousers, studio"
                progress = st.progress(0)
                def gen1(): return generate_image(p1, ref, img_model, api_key)
                def gen2(): return generate_image(p2, ref, img_model, api_key)
                with ThreadPoolExecutor(max_workers=2) as ex:
                    f1, f2 = ex.submit(gen1), ex.submit(gen2)
                    res = {}
                    for i, f in enumerate(as_completed([f1, f2])):
                        progress.progress((i+1)/2)
                        res["mannequin" if f==f1 else "model"] = f.result()
                progress.empty()
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Манекен")
                    if res.get("mannequin"):
                        st.image(res["mannequin"], use_container_width=True)
                        buf = io.BytesIO(); res["mannequin"].save(buf, "PNG")
                        st.download_button("Скачать", buf.getvalue(), "mannequin.png")
                    else: st.info("Не удалось")
                with c2:
                    st.subheader("Модель")
                    if res.get("model"):
                        st.image(res["model"], use_container_width=True)
                        buf = io.BytesIO(); res["model"].save(buf, "PNG")
                        st.download_button("Скачать", buf.getvalue(), "model.png")
                    else: st.info("Не удалось")

with tab2:
    st.header("Описание")
    scr = st.file_uploader("Загрузите скриншот", type=["jpg", "png"])
    if scr:
        img = Image.open(scr)
        st.image(img, use_container_width=True)
    if st.button("Сгенерировать описание"):
        if not api_key: st.error("Введите ключ")
        elif not scr: st.error("Загрузите скриншот")
        else:
            with st.spinner("..."):
                desc = generate_description("Анализируй скриншот и составь описание", img, text_model, api_key)
                if desc:
                    st.code(desc, language="markdown")
                    st.download_button("Скачать", desc, "description.txt")