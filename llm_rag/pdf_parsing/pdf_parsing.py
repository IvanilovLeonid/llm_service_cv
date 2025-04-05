import os
import PyPDF2
import requests
from groq import Groq
from typing import Dict
import json
from process_rag_cv import process_resume_with_matching

FOLDER_PATH = "/Users/lenaivanilov/Documents/project_llm/cvs"
# GROQ_API_KEY = "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"
GROQ_API_KEY = "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"
FASTAPI_URL = "http://localhost:8000/resumes/"

groq_client = Groq(api_key=GROQ_API_KEY)


def extract_text_from_pdf(pdf_path: str) -> str:
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
def parse_pdf_with_groq(pdf_text: str, pdf_path: str) -> Dict:

    prompt = (
        "Ты эксперт по парсингу резюме. Извлеки из текста следующие поля и запиши их строго как : "
        "full_name, direction, skills, experience.\n"
        f"В полях вводи строго то, что в самом тексте подходит под данный пункт. \n"
        "Обязательно следи чтобы ничего лишнего не попало.\n"
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

        print("изначальный вид:")
        print(parsed_json)

        parsed_json = process_resume_with_matching(parsed_json, "http://localhost:8000/vacancies/")
        print("как в базе данных")
        print(parsed_json)

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


def process_pdf_folder(folder_path: str):
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

            resume_data = parse_pdf_with_groq(pdf_text, pdf_path)
            if not resume_data:
                continue
            add_to_database(resume_data)


if __name__ == "__main__":
    process_pdf_folder(FOLDER_PATH)
