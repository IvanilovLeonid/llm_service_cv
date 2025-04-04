import streamlit as st
import subprocess
import os
import time
from voice_recording_backend import transcribe_audio
from text_editor import process_text, get_oauth_token, correct_text
from time import sleep
# Константы для API GigaChat
GIGACHAT_API_KEY = 'M2ZhMjE1ZmUtYTM5Yi00OTNkLTllMGUtYmEzZmJmNmFmZDU1OmE4OGJhNGY1LWI5OTgtNDFmOC04OWRjLWNjNzkyMmE4MzYyNA=='

def get_filename(extension="wav"):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"recording_{timestamp}.{extension}"

def start_recording():
    if st.session_state.get("recording", False):
        return

    st.session_state.recording = True
    st.session_state.filename = get_filename("wav")

    try:
        st.session_state.process = subprocess.Popen(
            ["ffmpeg", "-y", "-f", "avfoundation", "-i", ":0", st.session_state.filename],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        st.error("Ошибка: ffmpeg не найден! Установите ffmpeg и попробуйте снова.")
        st.session_state.recording = False

def stop_recording():
    if not st.session_state.get("recording", False):
        return

    process = st.session_state.get("process")
    if process:
        process.terminate()
        process.wait()

    st.session_state.recording = False
    st.session_state.audio_file = st.session_state.filename  # Сохраняем путь к .wav файлу

    # Вызываем process_inputVoise() для обновления состояния
    process_inputVoise()


#
# def process_inputVoise():
#     if st.session_state.get("audio_file"):
#         # Распознаем текст
#         transcription = transcribe_audio(st.session_state.audio_file)
#
#         if transcription:
#             # Получаем OAuth-токен для GigaChat
#             token = get_oauth_token(GIGACHAT_API_KEY)
#
#             # Исправляем текст с помощью correct_text
#             corrected_text = correct_text(transcription, token)
#
#             # Обрабатываем исправленный текст с помощью process_text
#             processed_text = process_text(corrected_text, token)
#
#             # Проверяем, что processed_text является словарем
#             if isinstance(processed_text, dict):
#                 # Обновляем историю сообщений
#                 st.session_state["chat_history"] = [
#                     f"### Вы отправили аудиофайл: {st.session_state.audio_file}",
#                     f"### Оригинальный текст: {transcription}",
#                     f"### Исправленный текст: {corrected_text}",
#                     f"### Ответ ИИ-помощника: {processed_text}"
#                 ]
#             else:
#                 st.session_state["chat_history"] = [
#                     f"### Вы отправили аудиофайл: {st.session_state.audio_file}",
#                     f"### Оригинальный текст: {transcription}",
#                     f"### Исправленный текст: {corrected_text}",
#                     "Ошибка: Некорректный формат ответа от process_text"
#                 ]
#         else:
#             st.session_state["chat_history"] = [
#                 f"### Вы отправили аудиофайл: {st.session_state.audio_file}",
#                 "Ошибка распознавания"
#             ]
#
#         st.session_state["chat_active"] = True
#         st.session_state["selected_vacancy"] = None
#         st.session_state["show_create_form"] = False
#         st.session_state["audio_file"] = None  # Очищаем аудиофайл после обработки


def process_inputVoise():
    """Обработка голосового ввода с активацией поиска вакансий"""
    if not st.session_state.get("audio_file"):
        return

    # Распознаем текст из аудио
    transcription = transcribe_audio(st.session_state.audio_file)
    if not transcription:
        st.session_state.update({
            "chat_active": True,
            "chat_history": ["Ошибка распознавания голоса"],
            "audio_file": None
        })
        return

    # Обработка текста через ИИ
    token = get_oauth_token(GIGACHAT_API_KEY)
    corrected_text = correct_text(transcription, token)
    sleep(1)
    processed_text = process_text(corrected_text, token)
    sleep(0.5)
    # Формируем поисковый запрос
    search_query = {
        "id": -1,  # ID для голосовых запросов
        "direction": "Результат голосового поиска",
        "skills": transcription,
        "tasks": corrected_text,
        "experience": "Не указано"
    }

    # Уточняем параметры поиска если ИИ вернул структурированные данные
    if isinstance(processed_text, dict) and 'corrected_keys' in processed_text:
        corrected = processed_text['corrected_keys']
        search_query.update({
            "direction": ', '.join(filter(lambda x: x != 'Не указано', corrected.get('direction', []))) or search_query[
                "direction"],
            "skills": ', '.join(filter(lambda x: x != 'Не указано', corrected.get('skills', []))) or transcription,
            "experience": ', '.join(
                filter(lambda x: x != 'Не указано', corrected.get('experience', []))) or "Не указано"
        })
    # Активируем поиск и обновляем интерфейс
    st.session_state.update({
        "selected_vacancy": search_query,
        "chat_active": False,  # Переключаем в режим результатов
        "audio_file": None,    # Очищаем файл
        "user_input": "",      # Очищаем текстовое поле
        "chat_history": []     # Очищаем историю (или оставляем минимальную информацию)
    })
    st.rerun()