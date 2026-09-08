if st.button("Сгенерировать"):
    if not api_key: st.error("Нет ключа")
    elif ref is None: st.error("Нет фото")
    else:
        prompt = f"Generate studio photo of {material} {item} on mannequin {part}"
        try:
            init_genai(api_key)
            model = genai.GenerativeModel(img_model)
            response = model.generate_content(
                [prompt, ref],
                generation_config=genai.types.GenerationConfig(response_modalities=["IMAGE"])
            )
            st.write("### Ответ API:")
            st.code(str(response), language="text")
            # ищем картинку...
            for part in response.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    st.image(img)
                    break
            else:
                st.error("Изображение не найдено в ответе")
        except Exception as e:
            st.error(f"Ошибка: {e}")