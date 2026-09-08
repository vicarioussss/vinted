import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="Fashion Generator", page_icon="👗", layout="wide")
st.title("👗 Генерация изображений одежды")

with st.sidebar:
    st.header("Настройки")
    api_key = st.text_input("🔑 Google Gemini API Key", type="password", placeholder="Введите ключ...")
    model_name = "gemini-2.0-flash-exp-image-generation"  # фиксировано

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📤 Загрузите фото вещи", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            ref_image = Image.open(uploaded_file)
            st.image(ref_image, caption="Референс", use_container_width=True)
        except:
            ref_image = None
            st.error("Не удалось загрузить изображение")
    else:
        ref_image = None

with col2:
    material = st.selectbox("Материал", ["leather", "wool", "cotton", "silk", "polyester", "denim"], index=0)
    item_type = st.selectbox("Тип вещи", ["blazer", "jacket", "coat", "dress", "skirt", "trousers", "shirt"], index=0)
    mannequin_part = st.selectbox("Часть манекена", ["torso", "full body"], index=0)

    if st.button("🚀 Сгенерировать изображение", use_container_width=True):
        if not api_key:
            st.error("❌ Введите API-ключ в боковой панели.")
        elif ref_image is None:
            st.error("❌ Загрузите изображение.")
        else:
            prompt = (
                f"Generate a high-resolution studio photo of this {material} {item_type}, "
                f"preserving every detail, on a headless/armless feminine cream linen mannequin {mannequin_part}, "
                f"turned three-quarters toward the left side of the frame with soft incoming light, "
                f"against a plain dark background"
            )

            st.info("⏳ Генерация... Пожалуйста, подождите.")
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)

                # ---------- ИСПРАВЛЕННЫЙ ВЫЗОВ ----------
                # Пробуем разные варианты для совместимости
                try:
                    # Способ 1: новый синтаксис (рекомендуемый)
                    response = model.generate_content(
                        [prompt, ref_image],
                        generation_config=genai.types.GenerateContentConfig(
                            response_modalities=['IMAGE']
                        )
                    )
                except AttributeError:
                    # Способ 2: старый синтаксис (если GenerateContentConfig не найден)
                    response = model.generate_content(
                        [prompt, ref_image],
                        generation_config={
                            "response_modalities": ["IMAGE"]
                        }
                    )

                # ---- ВЫВОД ОТВЕТА API (отладка) ----
                st.subheader("📦 Полный ответ от API:")
                st.code(str(response), language="text")

                # Извлекаем изображение
                generated_image = None
                for part in response.parts:
                    if part.inline_data is not None and part.inline_data.mime_type.startswith("image/"):
                        generated_image = Image.open(io.BytesIO(part.inline_data.data))
                        break

                if generated_image:
                    st.success("✅ Изображение сгенерировано!")
                    st.image(generated_image, use_container_width=True)
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Скачать",
                        data=buf.getvalue(),
                        file_name="generated.png",
                        mime="image/png"
                    )
                else:
                    st.error("❌ В ответе API не найдено изображение.")
                    if hasattr(response, 'text') and response.text:
                        st.warning(f"Текст ответа:\n{response.text}")

            except Exception as e:
                st.error(f"❌ Ошибка при вызове API: {e}")
                st.code(str(e), language="text")