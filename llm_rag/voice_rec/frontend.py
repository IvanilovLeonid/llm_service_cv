import streamlit as st
import pandas as pd
import uuid
from voice_recorder import start_recording, stop_recording, process_inputVoise
from text_editor import process_text, get_oauth_token

# Константы для API GigaChat
GIGACHAT_API_KEY = 'MDVhZjBkMWEtYjJjZS00ZmJjLTkzZjUtMjVlOGUwODdmNmY4OmYwYTI0NDNlLWU0NWItNGU1MS04NTg5LWYzNGY2ZDY1ZTBhMQ=='


def main():
    st.set_page_config(page_title="HR-Инструмент", layout="wide")

    # Кастомные стили для нежного дизайна
    st.markdown(
        """
        <style>
        @import url('@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

        /* Основные стили */
        body {
            font-family: 'Montserrat', sans-serif;
            background-color: #F5F0FA; /* Супер светлый фиолетовый фон для правой части */
            color: #5A5A5A;
        }
        h1, h2, h3 {
            font-family: 'Montserrat', serif;
            color: #7A6F8B; /* Тёмно-фиолетовый для заголовков */
        }
        .stButton>button {
            background-color: #A8A4CE !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stButton>button:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stTextInput>div>div>input {
            border-radius: 10px !important;
            border: 1px solid #D8B5D8 !important;
            padding: 10px !important;
        }
        .stTextArea>div>div>textarea {
            border-radius: 10px !important;
            border: 1px solid #D8B5D8 !important;
            padding: 10px !important;
        }
        .stSidebar {
            background-color: #7A6F8B !important; /* Тёмно-фиолетовый фон для бокового меню */
            box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05) !important;
            padding: 20px !important;
        }
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #FFFFFF !important; /* Белый текст для заголовков в боковом меню */
        }
        .stSidebar .stMarkdown {
            color: #FFFFFF !important; /* Белый текст для основного текста в боковом меню */
        }
        .stExpander {
            border: 1px solid #E0D7E9 !important;
            border-radius: 10px !important;
            margin-bottom: 10px !important;
        }
        .stExpander .stMarkdown {
            color: #7A6F8B !important; /* Тёмно-фиолетовый текст для раскрывающихся блоков */
        }
        .empty-list {
            color: #A8A4CE;
            font-style: italic;
        }
        .gradient-hr {
            border: 0;
            height: 1px;
            background: #E0D7E9;
            margin: 20px 0;
        }
        .card {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        /* Стили для радиокнопок */
        .stRadio>div>label>div>div {
            color: #7A6F8B !important;
        }
        /* Цвет текста на правой стороне */
        .stMarkdown {
            color: #7A6F8B !important; /* Тёмно-фиолетовый текст для правой части */
        }
        /* Стили для иконки микрофона */
        .microphone-icon {
            font-size: 20px;
            color: white;
        }
        /* Стили для иконки плюсика */
        .plus-icon {
            font-size: 20px;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Инициализация session_state
    for key, default in {
        "chat_history": [],
        "user_input": "",
        "chat_active": False,
        "show_create_form": False,
        "selected_vacancy": None,
        "vacancies": [],
        "recording": False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    with st.sidebar:
        # Большой заголовок "Инструменты эйчар"
        st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>HR-инструмент</h1>", unsafe_allow_html=True)
        st.markdown("<div class='gradient-hr'></div>", unsafe_allow_html=True)

        st.markdown("<h2 style='color: #FFFFFF;'>Ваш ИИ-помощник</h2>", unsafe_allow_html=True)
        # Текстовое поле и микрофон
        text_input_col, mic_col = st.columns([0.9, 0.1])
        with text_input_col:
            if not st.session_state.get("recording", False):
                user_input = st.text_input("", placeholder="Спросите что-нибудь...", label_visibility="collapsed",
                                           key="user_input", on_change=handle_enter)
            else:
                st.markdown("<p style='color: #FFFFFF; font-weight: bold;'>🔴 Слушаю Вас! Говорите...</p>",
                            unsafe_allow_html=True)

        with mic_col:
            if not st.session_state.get("recording", False):
                if st.button("🎤", key="mic_button"):
                    start_recording()
                    st.session_state["recording"] = True
                    st.rerun()
            else:
                if st.button("   ⏹   ", key="stop_mic_button"):
                    stop_recording()
                    st.session_state["recording"] = False
                    st.rerun()

        if st.session_state.get("recording", False):
            if st.button("Закончить и отправить", key="send_audio_button"):
                stop_recording()
                process_inputVoise()
                st.session_state["recording"] = False
                st.rerun()
        else:
            if st.button("Отправить", key="send_button"):
                process_input()

        # Пустая строка
        st.write("")

        # Заголовок "Список вакансий" и кнопка "+"
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown("<h2 style='color: #FFFFFF;'>Список вакансий</h2>", unsafe_allow_html=True)
        with col2:
            if st.button("➕", key="add_vacancy_sidebar"):
                st.session_state["show_create_form"] = True

        # Если список вакансий пуст
        if not st.session_state["vacancies"]:
            st.markdown("<p class='empty-list'>Тут пока пусто... Чтобы добавить вакансию, нажмите на плюсик.</p>",
                        unsafe_allow_html=True)
        else:
            for vacancy in st.session_state["vacancies"]:
                if st.button(vacancy["title"], key=f"vacancy_{vacancy['id']}"):
                    st.session_state["selected_vacancy"] = vacancy

    # Логика отображения правой части экрана
    if st.session_state["show_create_form"]:
        create_vacancy()
    elif st.session_state["selected_vacancy"]:
        show_vacancy_details(st.session_state["selected_vacancy"])
    elif st.session_state["chat_active"]:
        show_chat()
    else:
        st.markdown("""
           ## Что вы можете сделать сейчас? 

           1. **Выберите вакансию** из списка слева, чтобы просмотреть детали и кандидатов.
           2. **Создайте новую вакансию**, нажав на кнопку "+" в боковом меню.

           Нужна помощь? Вот несколько идей:
           - Спросите у ИИ-помощника: *"Сколько людей хотят на эту [должность]"*.
           - Или спросите: *"Какие кандидаты подходят для [название вакансии]?"*
           - Нужна помощь с описанием? Скажите: *"Помоги написать описание вакансии"*.

           ИИ-помощник всегда готов помочь! Просто начните вводить запрос или нажмите на микрофон, чтобы задать вопрос голосом.
           """)


def create_vacancy():
    st.subheader("Создание новой вакансии")

    # Поля для ввода данных
    title = st.text_input("Название вакансии*", placeholder="Введите название вакансии")
    skills = st.text_area("Требуемые навыки*", placeholder="Опишите необходимые навыки")
    experience = st.text_area("Опыт*", placeholder="Укажите требуемый опыт")
    description = st.text_area("Описание задач*", placeholder="Опишите задачи вакансии")

    # Кнопка "Создать вакансию"
    if st.button("Создать вакансию", key="create_vac"):
        # Проверка, что все поля заполнены
        if not title.strip():
            st.warning("Поле 'Название вакансии' обязательно для заполнения!")
        elif not skills.strip():
            st.warning("Поле 'Требуемые навыки' обязательно для заполнения!")
        elif not experience.strip():
            st.warning("Поле 'Опыт' обязательно для заполнения!")
        elif not description.strip():
            st.warning("Поле 'Описание задач' обязательно для заполнения!")
        else:
            # Если все поля заполнены, создаём новую вакансию
            new_vacancy = {
                "id": str(uuid.uuid4()),
                "title": title,
                "skills": skills,
                "experience": experience,
                "description": description
            }
            st.session_state["vacancies"].append(new_vacancy)
            st.session_state["show_create_form"] = False
            st.session_state["selected_vacancy"] = new_vacancy
            st.rerun()


def show_vacancy_details(vacancy):
    st.subheader(f"Вакансия: {vacancy['title']}")
    st.write(f"**Навыки:** {vacancy['skills']}")
    st.write(f"**Опыт:** {vacancy['experience']}")
    st.write(f"**Описание задач:** {vacancy['description']}")

    st.subheader("Подходящие кандидаты")
    candidates = [
        {"name": "Иван Иванов", "skills": "Python, Django", "experience": "3 года", "relevance": "85%",
         "resume": "ivan_ivanov.pdf"},
        {"name": "Анна Смирнова", "skills": "ML, Pandas", "experience": "2 года", "relevance": "78%",
         "resume": "anna_smirnova.pdf"}
    ]

    for candidate in candidates:
        with st.expander(f"{candidate['name']} - {candidate['relevance']}"):
            st.write(f"**Навыки:** {candidate['skills']}")
            st.write(f"**Опыт работы:** {candidate['experience']}")
            st.download_button(label="📄 Скачать резюме", data=b"", file_name=candidate["resume"],
                               mime="application/pdf")

    selected_candidate = st.radio("Выберите кандидата:", [c["name"] for c in candidates], index=None,
                                  key="selected_candidate")

    if st.button("Закрыть вакансию", key="close_vacancy",
                 disabled=st.session_state.get("selected_candidate") is None):
        st.session_state["vacancies"] = [v for v in st.session_state["vacancies"] if v["id"] != vacancy["id"]]
        st.session_state["candidates"] = [c for c in candidates if c["name"] != st.session_state["selected_candidate"]]
        del st.session_state["selected_vacancy"]
        del st.session_state["selected_candidate"]
        st.rerun()


def handle_enter():
    if st.session_state["user_input"]:
        process_input()


def process_input():
    user_input = st.session_state["user_input"].strip()
    if user_input:
        st.session_state["chat_history"] = [f"### Вы: {user_input}", "Место для вывода информации от нейронки..."]
        st.session_state["chat_active"] = True
        st.session_state["selected_vacancy"] = None  # Очищаем выбранную вакансию
        st.session_state["show_create_form"] = False  # Закрываем форму создания вакансии
        st.session_state["user_input"] = ""  # Очистка поля ввода

def process_input():
    """Обработка текстового ввода."""
    user_input = st.session_state["user_input"].strip()
    if user_input:
        # Получаем OAuth-токен для GigaChat
        token = get_oauth_token(GIGACHAT_API_KEY)

        # Обрабатываем текст с помощью text_editor
        processed_text = process_text(user_input, token)

        # Проверяем, что processed_text является словарем
        if isinstance(processed_text, dict):
            # Формируем сообщения для вывода
            messages = [
                f"### Ваш запрос: {user_input}",
                f"### Исправленный текст: {processed_text.get('corrected_text', 'Нет данных')}",
                f"### Ответ ИИ-помощника: {processed_text}"
            ]
        else:
            messages = [
                f"### Вы: {user_input}",
                "Ошибка: Некорректный формат ответа от process_text"
            ]

        # Обновляем историю сообщений
        st.session_state["chat_history"] = messages
        st.session_state["chat_active"] = True
        st.session_state["selected_vacancy"] = None  # Очищаем выбранную вакансию
        st.session_state["show_create_form"] = False  # Закрываем форму создания вакансии
        st.session_state["user_input"] = ""  # Очистка поля ввода

def show_chat():
    for message in st.session_state["chat_history"]:
        st.markdown(message)


def clear_main_view():
    st.session_state.update({"chat_active": False, "show_create_form": False, "selected_vacancy": None})


if __name__ == "__main__":
    main()