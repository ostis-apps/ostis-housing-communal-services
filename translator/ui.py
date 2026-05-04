from text_extractor import TextExtractor
from scs_generator import SCsGenerator
import streamlit as st
from pathlib import Path
import tempfile

class UI:
    def __init__(self):
        st.set_page_config(
            page_title="Транслятор текста в scs-код",
            page_icon="🔄",
            layout="wide"
        )

        st.title("🔄 Транслятор текста в SCS-код")
        st.markdown("Преобразование текста на естественном языке в scs-код")

        with st.sidebar:
            st.header("⚙️ Настройки")

            model_options = ["mistral", "phi3:mini", "qwen2.5-coder:7b", "Другое (введите название)"]
            selected = st.selectbox("Модель LLM", model_options)
            if selected == "Другое (введите название)":
                selected_model = st.text_input("Введите название модели", value="")
            else:
                selected_model = selected
            if not selected_model:
                st.warning("Выберите или введите модель")

            st.subheader("Параметры модели")
            num_ctx = st.slider(
                "Размер контекста (num_ctx)",
                min_value=2048,
                max_value=16384,
                value=4096,
                step=1024,
                help="Максимальное количество токенов, которое модель может обработать за раз. Больше = лучше для длинных текстов, но медленнее и требует больше памяти"
            )

            st.subheader("Параметры обработки")
            chunk_size = st.slider("Размер чанка (символов)", 200, 2000)
            chunk_overlap = st.slider("Перекрытие чанков (символов)", 50, 500)

            st.divider()
            st.info("💡 **Совет**: Для больших документов используйте меньший размер чанка")
            st.info("🔧 **Требования**: Установите Ollama и скачайте модель: `ollama pull " + selected_model + "`")

        tab1, tab2 = st.tabs(["📁 Загрузка файла", "✍️ Ввод текста"])

        text_content = ""
        file_name = None

        with tab1:
            uploaded_file = st.file_uploader(
                "Выберите файл",
                type=["txt", "pdf", "docx"],
                help="Поддерживаются форматы: .txt, .pdf, .docx"
            )

            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                try:
                    extractor = TextExtractor(tmp_path)
                    result = extractor.extract_text()
                    text_content = result["full_text"]
                    file_name = uploaded_file.name
                    st.success(f"✅ Файл '{file_name}' загружен")
                    with st.expander("📄 Предпросмотр текста"):
                        preview_text = text_content[:1000]
                        if len(text_content) > 1000:
                            preview_text += "...\n\n(Показано первых 1000 символов)"
                        st.text_area("Текст", preview_text, height=200)
                except Exception as e:
                    st.error(f"❌ Ошибка при чтении файла: {e}")
                finally:
                    Path(tmp_path).unlink(missing_ok=True)

        with tab2:
            text_input = st.text_area(
                "Введите текст",
                height=300,
                placeholder="Введите текст для преобразования в scs-код..."
            )
            if text_input:
                text_content = text_input
                file_name = "input"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_button = st.button(
                "🚀 Сгенерировать SCS-код",
                type="primary",
                use_container_width=True,
                disabled=not text_content
            )
        if generate_button and text_content:
            st.divider()
            st.header("📊 Результат генерации")
            progress_bar = st.progress(0)
            status_text = st.empty()
            try:
                status_text.text("🔄 Загрузка модели...")
                progress_bar.progress(10)
                generator = SCsGenerator(selected_model, num_ctx)
                status_text.text(f"📦 Разбиение текста на чанки (размер: {chunk_size})...")
                progress_bar.progress(20)
                chunks = TextExtractor.text_to_chunks(text_content, chunk_size, chunk_overlap)
                if len(chunks) % 10 == 1:
                    st.info(f"📊 Текст разбит на {len(chunks)} чанк (размер {chunk_size}, перекрытие {chunk_overlap})")
                elif 2 <= len(chunks) % 10 <= 4:
                    st.info(f"📊 Текст разбит на {len(chunks)} чанка (размер {chunk_size}, перекрытие {chunk_overlap})")
                else:
                    st.info(f"📊 Текст разбит на {len(chunks)} чанков (размер {chunk_size}, перекрытие {chunk_overlap})")
                scs_blocks = []
                for i, chunk in enumerate(chunks):
                    progress = 20 + int((i + 1) / len(chunks) * 70)
                    progress_bar.progress(progress)
                    status_text.text(f"🔄 Генерация SCS для чанка {i + 1}/{len(chunks)}...")
                    scs_block = generator.text_to_scs(chunk)
                    scs_blocks.append(scs_block)
                status_text.text("🔗 Объединение результатов...")
                progress_bar.progress(95)
                final_scs = "\n".join(scs_blocks)
                progress_bar.progress(100)
                status_text.text("✅ Готово!")
                with st.expander("📝 Сгенерированный SCS-код", expanded=True):
                    st.code(final_scs, language="scs", line_numbers=True)
                st.download_button(
                    label="💾 Скачать SCS-файл",
                    data=final_scs,
                    file_name="output.scs",
                    mime="text/plain",
                    use_container_width=True
                )
                st.success("🎉 Генерация успешно завершена!")
            except Exception as e:
                st.error(f"❌ Ошибка при генерации: {e}")
                st.info("Убедитесь, что Ollama запущен и модель скачана.\n\n"
                        f"Команда для скачивания: `ollama pull {selected_model}`")
            finally:
                progress_bar.empty()
                status_text.empty()
        elif generate_button and not text_content:
            st.warning("⚠️ Пожалуйста, загрузите файл или введите текст для генерации.")
        st.divider()
        st.caption("💡 Для работы приложения требуется запущенный сервер Ollama с выбранной моделью")