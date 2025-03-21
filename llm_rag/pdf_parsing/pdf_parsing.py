import os
import PyPDF2
import requests
from groq import Groq
from typing import Dict
import json

FOLDER_PATH = "/Users/lenaivanilov/Documents/project_llm/cv_files"
GROQ_API_KEY = "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"
FASTAPI_URL = "http://localhost:8000/resumes/"

groq_client = Groq(api_key=GROQ_API_KEY)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Извлекает текст из PDF-файла."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"Ошибка при чтении {pdf_path}: {e}")
        return ""

# TODO сделать через RAG тоже самое и с помощью него находить сходства
def parse_pdf_with_groq(pdf_text: str, pdf_path: str, directions_set: set) -> Dict:
    directions_list = sorted(directions_set)
    directions_string = ", ".join(directions_list)

    prompt = (
        "Ты эксперт по парсингу резюме. Извлеки из текста следующие поля и запиши их на русском языке: "
        "full_name, direction, skills, experience.\n"
        f"Поле direction должно строго соответствовать одному из следующих значений: {directions_string}.\n"
        "Верни результат в виде корректного JSON с такой структурой:\n"
        "{\n"
        "    \"full_name\": \"string\",\n"
        "    \"direction\": \"string\",\n"
        "    \"skills\": \"string\",\n"
        "    \"experience\": \"string\"\n"
        "}\n"
        "Не добавляй объяснений, комментариев или дополнительного текста — только JSON-объект."
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": pdf_text}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        # Получение ответа
        result = response.choices[0].message.content.strip()

        # Попытка исправить возможные проблемы с экранированными символами
        corrected_response = result.replace(r"\_", "_")
        print(corrected_response)
        # Попробуем преобразовать JSON
        parsed_json = json.loads(corrected_response)

        # Добавляем pdf_filename
        parsed_json["pdf_filename"] = pdf_path

        return parsed_json

    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        print(f"Полученный результат: {result}")
    except Exception as e:
        print(f"Общая ошибка при парсинге с Groq: {e}")

    # Возвращаем пустой словарь в случае ошибки
    return {}


def get_unique_directions_from_vacancies(api_url: str) -> set:
    """
    Получает уникальные направления (direction) из базы данных вакансий.

    :param api_url: URL для GET-запроса к вакансиям, например http://localhost:8000/vacancies/
    :return: Множество уникальных направлений
    """
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            vacancies = response.json()
            directions = [vacancy.get("direction") for vacancy in vacancies if vacancy.get("direction")]
            return set(directions)
        else:
            print(f"❌ Ошибка при получении данных: {response.status_code} - {response.text}")
            return set()
    except Exception as e:
        print(f"❌ Ошибка при запросе направлений вакансий: {e}")
        return set()



def add_to_database(parsed_data: Dict):
    url = "http://localhost:8000/resumes/"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=parsed_data)
        if response.status_code == 200:
            print("Резюме успешно добавлено в базу данных")
        else:
            print(f"Ошибка при добавлении в базу: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Ошибка при отправке данных: {e}")


def process_pdf_folder(folder_path: str, direction_set: set):
    """Обрабатывает все PDF-файлы в папке и добавляет их в базу данных."""
    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не существует")
        return

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"Обработка файла: {pdf_path}")

            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                continue

            resume_data = parse_pdf_with_groq(pdf_text, pdf_path, direction_set)
            if not resume_data:
                continue

            add_to_database(resume_data)


if __name__ == "__main__":
    directions = get_unique_directions_from_vacancies("http://localhost:8000/vacancies/")
    process_pdf_folder(FOLDER_PATH, directions)
