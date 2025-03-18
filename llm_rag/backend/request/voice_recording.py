from functools import partial
import pyaudio
import wave
import tempfile
import os
import time
import torch
import librosa
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import threading

# Параметры записи
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 60  # Максимальная длительность, можно прервать раньше

# Загрузка модели
MODEL_NAME = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)

# Глобальная переменная для управления записью
is_recording = True

def audio_callback(in_data, frame_count, time_info, status, frames):
    """Callback для потока записи с проверкой флага"""
    frames.append(in_data)
    return (in_data, pyaudio.paContinue if is_recording else pyaudio.paComplete)

def input_thread():
    """Поток для отслеживания нажатия Enter"""
    global is_recording
    input("Нажмите Enter для остановки записи...\n")
    is_recording = False

def record_audio():
    """Запись с возможностью досрочного завершения"""
    global is_recording
    is_recording = True
    frames = []

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=partial(audio_callback, frames=frames)  # Используем замыкание
    )

    print(f"Запись началась (максимум {RECORD_SECONDS} секунд)...")
    
    # Запуск потока для отслеживания ввода
    thread = threading.Thread(target=input_thread)
    thread.start()

    # Ожидание завершения записи
    start_time = time.time()
    while is_recording and time.time() - start_time < RECORD_SECONDS:
        time.sleep(0.1)

    # Остановка потока
    stream.stop_stream()
    stream.close()
    audio.terminate()
    is_recording = False

    # Сохранение во временный файл
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return temp_file.name


# Функция transcribe_audio осталась без изменений
def transcribe_audio(file_path):
    """Распознаёт речь с помощью Wav2Vec 2.0"""
    try:
        # Загрузка аудио
        audio_input, _ = librosa.load(file_path, sr=RATE)
        
        # Предобработка
        input_values = processor(
            audio_input, 
            return_tensors="pt",
            padding="longest",
            sampling_rate=RATE
        ).input_values
        
        # Инференс
        with torch.no_grad():
            logits = model(input_values).logits

        # Декодирование
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.decode(predicted_ids[0])
        
        return transcription
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return None
    finally:
        os.remove(file_path)  # Удаляем временный файл

if __name__ == "__main__":
    print("Подготовка к записи...")
    time.sleep(1)
    
    audio_file = record_audio()
    print("Распознавание...")
    
    text = transcribe_audio(audio_file)
    
    if text:
        print(f"Распознанный текст: {text}")
    else:
        print("Распознавание не удалось")