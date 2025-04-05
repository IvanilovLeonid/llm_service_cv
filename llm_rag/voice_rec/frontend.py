import streamlit as st
import requests  # Импортируем библиотеку для выполнения HTTP-запросов
from voice_recorder import start_recording, stop_recording, process_inputVoise
from text_editor import process_text, get_oauth_token
import pyttsx3
import threading
from typing import Dict, List
import time
import subprocess

# Константы для API GigaChat
GIGACHAT_API_KEY = 'MWI4YmEzOTAtYTQwMS00OGM5LTk3ODYtNDFlNjg1MTg1NTIzOmJkNDg3OTQ2LTQ3NTctNGYwNS1iMjg5LTVhNzIyYTVjOTc0NQ=='


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
        "temp_input": "",  # Новая временная переменная
        "chat_active": False,
        "show_create_form": False,
        "selected_vacancy": None,
        "vacancies": [],
        "recording": False,
        "vacancies_loaded": False,
        "audio_file": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Загрузка вакансий при первом запуске
    if not st.session_state["vacancies_loaded"]:
        st.session_state["vacancies"] = fetch_vacancies()
        st.session_state["vacancies_loaded"] = True
    if 'input_processed' not in st.session_state:
        st.session_state.input_processed = False

    with st.sidebar:
        st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>HR-инструмент</h1>", unsafe_allow_html=True)
        st.markdown("<div class='gradient-hr'></div>", unsafe_allow_html=True)

        st.markdown("<h2 style='color: #FFFFFF;'>Ваш ИИ-помощник</h2>", unsafe_allow_html=True)

        # Текстовое поле и микрофон
        text_input_col, mic_col = st.columns([0.9, 0.1])
        with text_input_col:
            if not st.session_state.get("recording", False):
                user_input = st.text_input(
                    "",
                    placeholder="Спросите что-нибудь...",
                    label_visibility="collapsed",
                    key="user_input",
                    value=st.session_state.get("temp_input", ""),
                    on_change=handle_enter
                )
                st.session_state.temp_input = ""  # Сброс после рендеринга
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
                if st.button("⏹", key="stop_mic_button"):
                    st.session_state["recording"] = False
                    st.rerun()
        # Кнопка отправки
        if st.session_state.get("recording", False):
            if st.button("Закончить и отправить", key="send_audio_button"):
                stop_recording()
                process_inputVoise()
                st.session_state["recording"] = False
                st.rerun()
        else:
            if st.button("Отправить", key="send_button"):
                process_text_input()

        # Блок вакансий (оставить без изменений)
        st.write("")
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown("<h2 style='color: #FFFFFF;'>Список вакансий</h2>", unsafe_allow_html=True)
        with col2:
            if st.button("➕", key="add_vacancy_sidebar"):
                st.session_state["show_create_form"] = True

        if not st.session_state["vacancies"]:
            st.markdown("<p class='empty-list'>Тут пока пусто...</p>", unsafe_allow_html=True)
        else:
            for vacancy in st.session_state["vacancies"]:
                if all(k in vacancy for k in ["direction", "skills", "tasks"]):
                    button_text = f"## {vacancy['direction']}\n\nНавыки: {vacancy['skills']}"
                    if st.button(button_text, key=f"vacancy_{vacancy['id']}", use_container_width=True):
                        st.session_state["selected_vacancy"] = vacancy

    # Основной контент
    if st.session_state["show_create_form"]:
        create_vacancy()
    elif st.session_state["selected_vacancy"]:
        show_vacancy_details(st.session_state["selected_vacancy"])
    elif st.session_state["chat_active"]:
        show_chat()
    else:
        st.markdown("""
            ## Что вы можете сделать сейчас?
            1. **Выберите вакансию** из списка слева
            2. **Создайте новую вакансию**, нажав на "+"
            3. **Задайте вопрос** через текстовое поле или микрофон
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

    if st.button("← Назад", key="back_to_main"):
        st.session_state["show_create_form"] = False
        st.rerun()

#
# def show_vacancy_details(vacancy):
#     st.subheader(f"Вакансия: {vacancy['direction']}")
#     st.write(f"**Навыки:** {vacancy['skills']}")
#     st.write(f"**Задачи:** {vacancy['tasks']}")
#
#     # Выполняем поиск резюме по вакансии
#     st.subheader("Подходящие кандидаты")
#     resumes = search_resumes(vacancy)
#
#     if not resumes:
#         st.markdown("<p class='empty-list'>Подходящих резюме не найдено.</p>", unsafe_allow_html=True)
#     else:
#         # Отображаем список резюме
#         for resume_data in resumes:
#             resume = resume_data["resume"]
#             similarity = resume_data["similarity"]
#
#             with st.expander(f"{resume['full_name']} - Совпадение: {similarity * 100:.2f}%"):
#                 st.write(f"**Навыки:** {resume['skills']}")
#                 st.write(f"**Опыт работы:** {resume['experience']}")
#
#                 col1, col2 = st.columns([1, 2])
#                 with col1:
#                     with open(resume["pdf_filename"], "rb") as pdf_file:
#                         pdf_bytes = pdf_file.read()
#                         st.download_button(
#                             label="📄 Скачать резюме",
#                             data=pdf_bytes,
#                             file_name=resume["pdf_filename"].split("/")[-1],
#                             mime="application/pdf"
#                         )
#                 with col2:
#                     if st.button("Закрыть вакансию с этим кандидатом",
#                                  key=f"close_with_{resume['id']}"):
#                         # Логика закрытия вакансии с выбранным кандидатом
#                         st.session_state["vacancies"] = [
#                             v for v in st.session_state["vacancies"]
#                             if v["id"] != vacancy["id"]
#                         ]
#                         st.session_state["selected_vacancy"] = None
#                         st.rerun()
#
#     # Кнопка для закрытия вакансии
#     if st.button("← Назад", key="back_to_main"):
#         st.session_state["selected_vacancy"] = None
#         st.rerun()

class VoiceAnnouncer:
    def __init__(self):
        self.lock = threading.Lock()
        self.engine = None
        self.russian_voice = None
        self.english_voice = None
        self._init_voices()

    def _init_voices(self):
        """Инициализация доступных голосов"""
        try:
            # Инициализация pyttsx3 голосов
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')

            for voice in voices:
                if not self.russian_voice and ('ru' in voice.languages or 'russian' in voice.name.lower()):
                    self.russian_voice = voice.id
                if not self.english_voice and ('en' in voice.languages or 'english' in voice.name.lower()):
                    self.english_voice = voice.id

            # Проверка системных голосов (для macOS/Linux)
            try:
                result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
                if 'ru_' in result.stdout or 'russian' in result.stdout.lower():
                    self.russian_voice = 'system'
            except:
                pass

        except Exception as e:
            print(f"Voice initialization error: {e}")

    def _speak_with_pyttsx3(self, text: str) -> bool:
        """Озвучивание через pyttsx3"""
        if not self.engine:
            return False

        try:
            with self.lock:
                # Пробуем русский голос, потом английский
                if self.russian_voice:
                    self.engine.setProperty('voice', self.russian_voice)
                elif self.english_voice:
                    self.engine.setProperty('voice', self.english_voice)

                self.engine.say(text)
                self.engine.runAndWait()
                return True
        except RuntimeError as e:
            print(f"Pyttsx3 runtime error: {e}")
            self.engine = None
            return False
        except Exception as e:
            print(f"Pyttsx3 error: {e}")
            return False

    def _speak_with_system(self, text: str) -> bool:
        """Озвучивание через системные средства"""
        try:
            # Пробуем русский голос, потом английский
            voices_to_try = []
            if self.russian_voice == 'system':
                voices_to_try.extend(['ru_RU', 'russian', 'Yuri'])
            voices_to_try.extend(['en_US', 'english', 'Alex'])

            for voice in voices_to_try:
                try:
                    subprocess.run(['say', '-v', voice, text], check=True)
                    return True
                except subprocess.CalledProcessError:
                    continue

            return False
        except Exception as e:
            print(f"System TTS error: {e}")
            return False

    def speak(self, text: str) -> bool:
        """Основной метод озвучивания"""
        # Сначала пробуем pyttsx3
        if self._speak_with_pyttsx3(text):
            return True

        # Если не получилось, пробуем системный способ
        if self._speak_with_system(text):
            return True

        print(f"All TTS methods failed for: {text}")
        return False


# Глобальный экземпляр
announcer = VoiceAnnouncer()


def announce_results(resumes: List[Dict]):
    """Озвучивает результаты поиска"""
    if not resumes:
        announcer.speak("No suitable candidates found")
        return

    count = len(resumes)
    announcer.speak(f"Found {count} candidates")

    time.sleep(0.5)

    for i, resume in enumerate(resumes, 1):
        name = resume['resume'].get('full_name', 'Unnamed candidate')
        similarity = round(resume['similarity'] * 100)
        text = f"Candidate {i}: {name}. Match: {similarity} percent"
        if not announcer.speak(text):
            print(f"Failed to announce: {text}")
        time.sleep(0.3)


def show_vacancy_details(vacancy):
    st.subheader(f"Vacancy: {vacancy['direction']}")
    st.write(f"**Skills:** {vacancy['skills']}")
    st.write(f"**Tasks:** {vacancy['tasks']}")

    # Выполняем поиск резюме по вакансии
    st.subheader("Suitable candidates")
    resumes = search_resumes(vacancy)

    # Кнопка озвучивания с обработкой в отдельном потоке
    if st.button("🔊 Announce results", key="speak_results"):
        threading.Thread(
            target=announce_results,
            args=(resumes,),
            daemon=True
        ).start()

    # Остальной код отображения...
    if not resumes:
        st.markdown("<p class='empty-list'>No suitable resumes found.</p>", unsafe_allow_html=True)
    else:
        for resume_data in resumes:
            resume = resume_data["resume"]
            similarity = resume_data["similarity"]

            with st.expander(f"{resume['full_name']} - Match: {similarity * 100:.2f}%"):
                st.write(f"**Skills:** {resume['skills']}")
                st.write(f"**Experience:** {resume['experience']}")

                col1, col2 = st.columns([1, 2])
                with col1:
                    with open(resume["pdf_filename"], "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="📄 Download resume",
                            data=pdf_bytes,
                            file_name=resume["pdf_filename"].split("/")[-1],
                            mime="application/pdf"
                        )
                with col2:
                    if st.button("Hire this candidate",
                                 key=f"close_with_{resume['id']}"):
                        st.session_state["vacancies"] = [
                            v for v in st.session_state["vacancies"]
                            if v["id"] != vacancy["id"]
                        ]
                        st.session_state["selected_vacancy"] = None
                        st.rerun()

    if st.button("← Back", key="back_to_main"):
        st.session_state["selected_vacancy"] = None
        st.rerun()


# При завершении приложения

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
    """Обработчик нажатия Enter в текстовом поле"""
    if st.session_state.get("user_input", ""):
        process_text_input()



def process_text_input():
    """Обработка текстового ввода с корректным формированием запроса"""
    current_input = st.session_state.user_input

    if not current_input:
        return

    # Получаем токен и обрабатываем текст
    token = get_oauth_token(GIGACHAT_API_KEY)
    processed_text = process_text(current_input, token)

    # Формируем базовую структуру запроса
    search_query = {
        "id": -1,  # Специальный ID для запросов
        "direction": "Результат поиска",
        "skills": current_input,
        "tasks": "",
        "experience": "Не указано"
    }

    # Если ответ содержит структурированные данные
    if isinstance(processed_text, dict):
        # Используем исправленный текст как описание
        search_query["tasks"] = processed_text.get('corrected_text', current_input)

        # Если есть исправленные ключи, используем их для поиска
        if 'corrected_keys' in processed_text:
            corrected = processed_text['corrected_keys']
            if corrected.get('direction'):
                search_query["direction"] = ', '.join([d for d in corrected['direction'] if d != 'Не указано'])
            if corrected.get('skills'):
                search_query["skills"] = ', '.join([s for s in corrected['skills'] if s != 'Не указано'])
            if corrected.get('experience'):
                search_query["experience"] = ', '.join([e for e in corrected['experience'] if e != 'Не указано'])
    else:
        search_query["tasks"] = str(processed_text)

    # Убираем пустые значения
    search_query = {k: v if v else "Не указано" for k, v in search_query.items()}

    # Активируем поиск
    st.session_state.selected_vacancy = search_query
    st.session_state.chat_active = False
    # st.session_state.user_input = ""  # Очищаем поле ввода
    st.rerun()  # Обновляем интерфейс

def show_chat():
    for message in st.session_state["chat_history"]:
        st.markdown(message)


def clear_main_view():
    st.session_state.update({"chat_active": False, "show_create_form": False, "selected_vacancy": None})


if __name__ == "__main__":
    main()