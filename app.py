import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re
import time

st.set_page_config(page_title="Fashion Generator", page_icon="👗", layout="wide")
st.title("👗 Генерация изображений одежды")

# Список моделей для генерации изображений (от более дешёвых к более дорогим)
IMAGE_MODELS = [
    "models/gemini-3.1-flash-image",      # рекомендую для экономии квоты
    "models/gemini-2.5-flash-image",
    "models/gemini-3.1-flash-image-preview",
    "models/gemini-3-pro-image-preview",
    "models/gemini-3-pro-image",
    "models/nano-banana-pro-preview",
]

# Инициализация сессионных переменных
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0
if "last_quota_error" not in st.session_state:
    st.session_state.last_quota_error = None

with st.sidebar:
    st.header("Настройки")
    api_key = st.text_input("🔑 Google Gemini API Key", type="password", placeholder="Введите ключ...")
    
    # Выбор модели
    img_model_name = st.selectbox(
        "🖼️ Модель для генерации изображений",
        options=IMAGE_MODELS,
        index=0,
        help="Выберите модель. Для экономии квоты используйте flash-модели."
    )
    
    # Отображение счётчика
    st.markdown("---")
    st.metric("📊 Использовано генераций в этой сессии", st.session_state.generation_count)
    if st.session_state.last_quota_error:
        st.warning(f"⏳ Квота исчерпана. Повторите попытку через {st.session_state.last_quota_error} секунд.")
    
    # Кнопка для сброса счётчика (опционально)
    if st.button("🔄 Сбросить счётчик"):
        st.session_state.generation_count = 0
        st.session_state.last_quota_error = None
        st.experimental_rerun()
    
    st.markdown("---")
    if st.button("📋 Показать все доступные модели (с generateContent)"):
        if not api_key:
            st.error("Сначала введите API-ключ.")
        else:
            try:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                st.subheader("Все модели (поддерживающие generateContent):")
                for m in models:
                    if 'generateContent' in m.supported_generation_methods:
                        st.write(f"- {m.name}")
            except Exception as e:
                st.error(f"Ошибка: {e}")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📤 Загрузите фото вещи (референс)", type=["jpg", "jpeg", "png"])
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
    use_reference = st.checkbox("Использовать референсное фото", value=True, help="Если снять галочку, генерация будет только по текстовому промпту.")

    if st.button("🚀 Сгенерировать изображение", use_container_width=True):
        if not api_key:
            st.error("❌ Введите API-ключ в боковой панели.")
        elif ref_image is None and use_reference:
            st.error("❌ Загрузите изображение или отключите использование референса.")
        else:
            # Базовый промпт (упрощённый)
            prompt = (
                f"Generate a high-resolution studio photo of a {material} {item_type} "
                f"on a headless/armless mannequin {mannequin_part}, "
                f"turned three-quarters to the left, soft lighting, plain dark background."
            )
            if not use_reference:
                prompt = (
                    f"Generate a high-resolution studio photo of a {material} {item_type} "
                    f"on a mannequin {mannequin_part}, dark background, soft studio lighting, photorealistic."
                )

            st.info("⏳ Генерация... Пожалуйста, подождите.")
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(img_model_name)

                content = [prompt, ref_image] if (use_reference and ref_image is not None) else prompt

                # Пробуем разные способы передачи response_modalities
                try:
                    response = model.generate_content(
                        content,
                        generation_config=genai.types.GenerateContentConfig(
                            response_modalities=['IMAGE']
                        )
                    )
                except (AttributeError, TypeError):
                    response = model.generate_content(
                        content,
                        generation_config={"response_modalities": ["IMAGE"]}
                    )

                # Отладка
                st.subheader("📦 Ответ API (часть):")
                resp_str = str(response)
                st.code(resp_str[:1500] + ("..." if len(resp_str)>1500 else ""), language="text")

                # Проверка на finish_reason
                blocked = False
                if hasattr(response, 'candidates') and response.candidates:
                    for cand in response.candidates:
                        if cand.finish_reason == 16:
                            blocked = True
                            st.warning("⚠️ Запрос заблокирован системой безопасности. Попробуйте упростить промпт или отключить референс.")

                if not blocked:
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
                        # Увеличиваем счётчик
                        st.session_state.generation_count += 1
                        st.session_state.last_quota_error = None
                    else:
                        st.error("❌ В ответе API не найдено изображение.")
                        if hasattr(response, 'text') and response.text:
                            st.warning(f"Текст ответа:\n{response.text}")
                        if "404" in resp_str or "not found" in resp_str:
                            st.info("💡 Модель не найдена. Попробуйте выбрать другую из списка.")

            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Ошибка при вызове API: {e}")
                st.code(error_msg, language="text")
                
                # Обработка ошибки 429 (Quota exceeded)
                if "429" in error_msg or "quota" in error_msg.lower():
                    # Пытаемся извлечь retry_delay
                    delay_match = re.search(r"retry_delay\s*{\s*seconds:\s*(\d+)", error_msg)
                    if delay_match:
                        delay_seconds = int(delay_match.group(1))
                        st.session_state.last_quota_error = delay_seconds
                        st.warning(f"⏳ Квота исчерпана. Повторите попытку через {delay_seconds} секунд.")
                        # Рекомендуем переключиться на более дешёвую модель
                        st.info("💡 Попробуйте выбрать более дешёвую модель (например, gemini-3.1-flash-image) и повторить запрос.")
                    else:
                        st.session_state.last_quota_error = 60  # примерное время
                        st.warning("⏳ Квота исчерпана. Подождите минуту и попробуйте снова.")
                else:
                    # Другие ошибки
                    st.session_state.last_quota_error = None