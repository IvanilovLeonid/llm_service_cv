from functools import partial
import pyaudio
import wave
import tempfile
import os
import time
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, pipeline
import threading
import torchaudio

# Параметры записи
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 60

# Загрузка модели для русского языка
MODEL_NAME = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
model.eval()

# Глобальная переменная для управления записью
is_recording = True


def audio_callback(in_data, frame_count, time_info, status, frames):
    frames.append(in_data)
    return in_data, pyaudio.paContinue if is_recording else pyaudio.paComplete


def input_thread():
    global is_recording
    input("Нажмите Enter для остановки записи...\n")
    is_recording = False


def record_audio():
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
        stream_callback=partial(audio_callback, frames=frames)
    )

    print(f"Запись началась (максимум {RECORD_SECONDS} секунд)...")
    thread = threading.Thread(target=input_thread)
    thread.start()

    start_time = time.time()
    while is_recording and time.time() - start_time < RECORD_SECONDS:
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    is_recording = False

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return temp_file.name


def transcribe_audio(file_path):
    """Распознаёт речь на русском языке"""
    try:
        waveform, sample_rate = torchaudio.load(file_path)

        if sample_rate != RATE:
            waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=RATE)(waveform)

        audio_input = waveform.squeeze().numpy()

        input_values = processor(audio_input, return_tensors="pt", sampling_rate=RATE).input_values

        with torch.no_grad():
            logits = model(input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

        return transcription.lower()
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return None
    finally:
        os.remove(file_path)


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