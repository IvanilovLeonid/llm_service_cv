import streamlit as st
import requests  # Импортируем библиотеку для выполнения HTTP-запросов
from voice_recorder import start_recording, stop_recording, process_inputVoise
from text_editor import process_text, get_oauth_token

# Константы для API GigaChat
GIGACHAT_API_KEY = 'NWMwOWI4ZGItYTY0OS00NjIwLWFjYzgtMjk2ZWY3ZTU0ZTcyOmY4YTNjNGRlLWE1MTEtNGJjMi05NTE5LTJmY2E1MWNhN2FlZQ=='


def fetch_vacancies():
    """Выполняет GET-запрос к API для получения списка вакансий."""
    try:
        response = requests.get("http://localhost:8000/vacancies/")
        if response.status_code == 200:
            return response.json()  # Возвращаем JSON с вакансиями
        else:
            st.error(f"Ошибка при загрузке вакансий: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Ошибка при выполнении запроса: {e}")
        return []


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
        "recording": False,
        "vacancies_loaded": False  # Флаг для проверки загрузки вакансий
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Загрузка вакансий при первом запуске
    if not st.session_state["vacancies_loaded"]:
        st.session_state["vacancies"] = fetch_vacancies()
        st.session_state["vacancies_loaded"] = True

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
                # Проверяем, что ключи "direction", "skills" и "tasks" существуют
                if "direction" in vacancy and "skills" in vacancy and "tasks" in vacancy:
                    # Формируем текст для кнопки
                    button_text = f"{vacancy['direction']}\nНавыки: {vacancy['skills']}\nЗадачи: {vacancy['tasks']}"
                    if st.button(button_text, key=f"vacancy_{vacancy['id']}"):
                        st.session_state["selected_vacancy"] = vacancy
                else:
                    st.error(f"Ошибка: Вакансия с ID {vacancy.get('id', 'неизвестно')} содержит неполные данные.")
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

    # Поля для ввода данных (без поля "Опыт")
    direction = st.text_input("Название вакансии*", placeholder="Введите название вакансии")
    skills = st.text_area("Требуемые навыки*", placeholder="Опишите необходимые навыки")
    tasks = st.text_area("Описание задач*", placeholder="Опишите задачи вакансии")

    # Кнопка "Создать вакансию"
    if st.button("Создать вакансию", key="create_vac"):
        # Проверка, что все поля заполнены
        if not direction.strip():
            st.warning("Поле 'Название вакансии' обязательно для заполнения!")
        elif not skills.strip():
            st.warning("Поле 'Требуемые навыки' обязательно для заполнения!")
        elif not tasks.strip():
            st.warning("Поле 'Описание задач' обязательно для заполнения!")
        else:
            # Формируем JSON для POST-запроса
            new_vacancy = {
                "direction": direction,
                "skills": skills,
                "tasks": tasks
            }

            # Отправляем POST-запрос на сервер
            try:
                response = requests.post(
                    "http://localhost:8000/vacancies/",
                    json=new_vacancy,
                    headers={"Content-Type": "application/json"}
                )

                # Проверяем успешность запроса
                if response.status_code == 200:  # 201 - Created
                    st.success("Вакансия успешно создана!")
                    # Обновляем список вакансий
                    st.session_state["vacancies"] = fetch_vacancies()
                    st.session_state["show_create_form"] = False
                    st.rerun()
                else:
                    st.error(f"Ошибка при создании вакансии: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка при отправке запроса: {e}")


def show_vacancy_details(vacancy):
    st.subheader(f"Вакансия: {vacancy['direction']}")
    st.write(f"**Навыки:** {vacancy['skills']}")
    st.write(f"**Задачи:** {vacancy['tasks']}")

    # Выполняем поиск резюме по вакансии
    st.subheader("Подходящие кандидаты")
    resumes = search_resumes(vacancy)

    if not resumes:
        st.markdown("<p class='empty-list'>Подходящих резюме не найдено.</p>", unsafe_allow_html=True)
    else:
        # Отображаем список резюме
        for resume_data in resumes:
            resume = resume_data["resume"]
            similarity = resume_data["similarity"]

            with st.expander(f"{resume['full_name']} - Совпадение: {similarity * 100:.2f}%"):
                st.write(f"**Навыки:** {resume['skills']}")
                st.write(f"**Опыт работы:** {resume['experience']}")


                with open(resume["pdf_filename"], "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    st.download_button(
                        label="📄 Скачать резюме",
                        data=pdf_bytes,
                        file_name=resume["pdf_filename"].split("/")[-1],
                        mime="application/pdf"
                    )

    # Кнопка для закрытия вакансии
    if st.button("← Назад", key="back_to_main"):
        st.session_state["selected_vacancy"] = None
        st.rerun()


def search_resumes(vacancy):
    """Выполняет POST-запрос для поиска резюме по вакансии."""
    try:
        # Формируем JSON для запроса
        search_data = {
            "direction": vacancy["direction"],
            "skills": vacancy["skills"],
            "tasks": vacancy["tasks"]
        }

        # Отправляем POST-запрос
        response = requests.post(
            "http://localhost:8000/search_resumes/",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )

        # Проверяем успешность запроса
        if response.status_code == 200:
            return response.json()  # Возвращаем список резюме
        else:
            st.error(f"Ошибка при поиске резюме: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Ошибка при выполнении запроса: {e}")
        return []


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