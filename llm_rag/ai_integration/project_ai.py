import re
import requests
import uuid

# Отключаем предупреждения SSL
requests.packages.urllib3.disable_warnings()

# Константы для API GigaChat
GIGACHAT_API_KEY = "M2ZhMjE1ZmUtYTM5Yi00OTNkLTllMGUtYmEzZmJmNmFmZDU1OmE4OGJhNGY1LWI5OTgtNDFmOC04OWRjLWNjNzkyMmE4MzYyNA=="
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

# Обновленные тематики с русскими названиями полей
THEMES = {
    "вакансии": ["направление", "навыки", "задачи"],
    "резюме": ["направление", "навыки", "опыт работы"]
}


def get_oauth_token(api_key):
    """Получает OAuth-токен для доступа к API GigaChat."""
    rq_uid = str(uuid.uuid4())
    headers = {
        "Authorization": f"Basic {api_key}",
        "RqUID": rq_uid,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    try:
        response = requests.post(AUTH_URL, headers=headers, data=data, verify=False)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при получении токена: {str(e)}") from e


def call_gigachat_api(prompt, token):
    """Отправляет запрос к API GigaChat и возвращает очищенный ответ."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # Снижаем температуру для точности
        "max_tokens": 256
    }
    try:
        response = requests.post(GIGACHAT_API_URL, headers=headers, json=data, verify=False)
        response.raise_for_status()
        raw_text = response.json()["choices"][0]["message"]["content"].strip()
        return clean_response(raw_text)
    except requests.exceptions.SSLError as e:
        raise Exception("Ошибка SSL: проверьте сертификаты.") from e
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Ошибка HTTP: {response.status_code}, {response.text}") from e
    except Exception as e:
        raise Exception(f"Неизвестная ошибка: {str(e)}") from e


def clean_response(text):
    """Удаляет маркировку списков и лишние пояснения из ответа."""
    # Удаляем нумерацию и символы списков
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'[\n\t]+', ' ', text)
    # Удаляем общие фразы-заглушки
    text = re.sub(r'Этот список может варьироваться.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Ключевые навыки:\s*', '', text, flags=re.IGNORECASE)
    return text.strip()


def determine_theme(text, token):
    """Улучшенная классификация с четкими инструкциями."""
    prompt = f"""
    Классифицируй текст как вакансию или резюме. Ответь только одним словом: вакансии, резюме или другое.
    Примеры:
    - "Требуется Python-разработчик" → вакансии
    - "Ищу работу: 3 года опыта" → резюме
    - "Резюме: Менеджер проектов" → резюме
    - "Срочно нужен специалист по DevOps!" → вакансии

    Текст: {text}
    """
    response = call_gigachat_api(prompt, token)
    return response.lower()


def extract_keywords_with_gigachat(text, fields, token):
    """Точное извлечение ключевых слов из исходного текста."""
    keywords = {}
    for field in fields:
        if field == "направление":
            prompt = f"Из текста: '{text}' извлеки основное направление деятельности (1-2 слова). Пример: 'Python-разработчик', 'Java-специалист'. Если нет - оставь пустым."
        elif field == "навыки":
            prompt = f"Из текста: '{text}' перечисли только явно указанные навыки через запятую. Пример: 'Python, Django, Flask'. Если нет - оставь пустым."
        elif field == "опыт работы":
            prompt = f"Из текста: '{text}' извлеки только явно указанный опыт работы (например: '3 года', '5 лет в IT'). Если нет - оставь пустым."
        elif field == "задачи":
            prompt = f"Из текста: '{text}' извлеки только явно указанные задачи через запятую. Пример: 'разработка api-сервисов'. Если нет - оставь пустым."
        else:
            continue

        response = call_gigachat_api(prompt, token)
        keywords[field] = [kw.strip() for kw in response.split(",") if kw.strip()]
    return keywords


def process_text(text, token):
    """Основная функция обработки текста."""
    if not text or len(text.strip()) < 10:
        return "Текст некорректен. Проверьте ввод."

    theme = determine_theme(text, token)

    if theme == "другое":
        return "Вопрос не входит в компетенцию."

    # Извлекаем ключевые слова с жесткой фильтрацией
    fields = THEMES[theme]
    keywords = extract_keywords_with_gigachat(text, fields, token)

    # Фильтруем пустые списки
    filtered_keywords = {k: v for k, v in keywords.items() if v}

    return {"flag": theme, "keywords": filtered_keywords}


# Примеры использования
if __name__ == "__main__":
    examples = [
        "Ищу работу Python-разработчиком. Опыт работы 3 года. Владею Django и Flask.",
        "Требуется Java-разработчик в компанию 'Альфа-Банк'. Задачи: разработка api-сервисов.",
        "Резюме: Менеджер проектов с 5-летним опытом в IT. Навыки: Agile, Scrum.",
        "Срочно нужен специалист по кибербезопасности! Зарплата от 150 тыс.",
        "Ищу работу: 3 года опыта в тестировании ПО. Инструменты: Selenium, Postman."
    ]

    try:
        token = get_oauth_token(GIGACHAT_API_KEY)
        for example in examples:
            print(f"\nТекст: {example}")
            result = process_text(example, token)
            print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")