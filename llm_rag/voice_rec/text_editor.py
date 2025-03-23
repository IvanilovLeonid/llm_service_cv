import re
import requests
import uuid

# Отключаем предупреждения SSL
requests.packages.urllib3.disable_warnings()

# Константы для API GigaChat
GIGACHAT_API_KEY = 'MDVhZjBkMWEtYjJjZS00ZmJjLTkzZjUtMjVlOGUwODdmNmY4OmYwYTI0NDNlLWU0NWItNGU1MS04NTg5LWYzNGY2ZDY1ZTBhMQ=='
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

# Словарь замен для специфичных опечаток
REPLACEMENTS = {
    r'(?i)(поэтом|паитон|питон|Pyton)': 'Python',
    r'(?i)(скл|СКЛ)': 'SQL',
    r'(?i)(джава|Java\s*script)': 'JavaScript',
    r'(?i)(фронтент|фронтенд|фронд)': 'Frontend',
    r'(?i)(быкент|бэкенд|бекенд)': 'Backend',
    r'(?i)(девопс|девопс-инженер)': 'DevOps',
    r'(?i)(мидл|мидл-плюс)': 'Middle+',
    r'(?i)(джун|джуниор)': 'Junior',
    r'(?i)(сеньор|синьор)': 'Senior',
    r'(?i)(фуллстак|фулстэк)': 'Fullstack',
    r'(?i)(машинное\s+обучение|мл)': 'Machine Learning',
    r'(?i)(искуственный\s+интеллект|ИИ)': 'Artificial Intelligence'
}

# Обновленные тематики с русскими названиями полей
THEMES = {
    "вакансии": ["направление", "навыки", "задачи"],
    "резюме": ["направление", "навыки", "опыт работы"]
}

# Словарь перевода ключей на английский
KEY_TRANSLATION = {
    "направление": "direction",
    "навыки": "skills",
    "опыт работы": "experience",
    "задачи": "tasks"
}


def translate_keys(data, translation_dict):
    """Переводит ключи словаря по заданному соответствию"""
    return {
        translation_dict.get(k, k): v
        for k, v in data.items()
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
        "temperature": 0.1,
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
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'[\n\t]+', ' ', text)
    text = re.sub(r'Этот список может варьироваться.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Ключевые навыки:\s*', '', text, flags=re.IGNORECASE)
    return text.strip()


def replace_context_words(text):
    """Замена специфичных опечаток и сокращений"""
    for pattern, replacement in REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def check_it_theme(text, token):
    """Проверяет принадлежность текста к IT-программированию"""
    prompt = f"""
    Относится ли этот текст к сфере IT-программирования или смежным технологиям?
    Ответь только 'да' или 'нет' без пояснений.

    Примеры IT-тем:
    - Разработка ПО
    - Вакансии программистов
    - Резюме IT-специалистов
    - Технические навыки (Python, SQL и т.д.)
    - Задачи по разработке

    НЕ IT-темы:
    - Грузоперевозки
    - Финансовые услуги
    - Медицинские услуги
    - Продажи

    Текст: {text}
    Ответ:
    """
    response = call_gigachat_api(prompt, token)
    return response.strip().lower() == 'да'


def correct_text(text, token):
    """Исправляет грамматику и опечатки в тексте с учетом контекста."""
    prompt = f"""
    Исправь грамматические ошибки и опечатки в тексте, сохранив исходный смысл.
    Текст: {text}
    Исправленный текст:
    """
    response = call_gigachat_api(prompt, token)
    return response.strip()


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
            prompt = f"Из текста: '{text}' извлеки только явно указанный опыт работы (например: '3 года', '5 лет'). Если нет - оставь пустым."
        elif field == "задачи":
            prompt = f"Из текста: '{text}' извлеки только явно указанные задачи через запятую. Пример: 'разработка backend-сервисов'. Если нет - оставь пустым."
        else:
            continue

        response = call_gigachat_api(prompt, token)
        keywords[field] = [kw.strip() for kw in response.split(",") if kw.strip()]
    return keywords


def process_text(text, token):
    """Основная функция обработки текста."""
    original_text = text.strip()
    if not original_text or len(original_text) < 10:
        return {"corrected_text": "Текст некорректен. Проверьте ввод.", "flag": "другое", "corrected_keys": {}}

    # 1. Замена специфичных опечаток
    context_corrected_text = replace_context_words(original_text)

    # 2. Проверка IT-тематики
    if not check_it_theme(context_corrected_text, token):
        return {"corrected_text": "Извините, ваш запрос не входит в мои компетенции", "flag": "другое", "corrected_keys": {}}

    # 3. Глубокая коррекция через GigaChat
    corrected_text = correct_text(context_corrected_text, token)

    # 4. Классификация
    theme = determine_theme(corrected_text, token)

    if theme == "другое":
        return {"corrected_text": "Вопрос не входит в компетенцию.", "flag": "другое", "corrected_keys": {}}

    # 5. Извлечение ключевых слов
    fields = THEMES[theme]
    keywords = extract_keywords_with_gigachat(corrected_text, fields, token)

    # 6. Формирование corrected_keys с проверкой на отсутствие данных
    corrected_keywords = {}
    for field in fields:
        if field in keywords and keywords[field]:
            # Проверка на "отсебятину" через кросс-валидацию с исправленным текстом
            valid_values = []
            for value in keywords[field]:
                if re.search(r'\b' + re.escape(value) + r'\b', corrected_text, re.IGNORECASE):
                    valid_values.append(value)
            corrected_keywords[field] = valid_values if valid_values else ["Не указано"]
        else:
            corrected_keywords[field] = ["Не указано"]

    # 7. Перевод ключей на английский
    translated_keywords = translate_keys(corrected_keywords, KEY_TRANSLATION)

    return {
        "original_text": original_text,
        "corrected_text": corrected_text,
        "flag": theme,
        "corrected_keys": translated_keywords
    }

# Примеры использования
if __name__ == "__main__":
    examples = [
        "Ищу работу Python-разработчиком. Опыт работы 3 года. Владею Django и Flask.",
        "Требуется Java-разработчик в компанию 'Альфа-Банк'. Задачи: разработка backend-сервисов.",
        "Резюме: Менеджер проектов с 5-летним опытом в IT. Навыки: Agile, Scrum.",
        "Срочно нужен специалист по кибербезопасности! Зарплата от 150 тыс.",
        "Ищу работу: 3 года опыта в тестировании ПО. Инструменты: Selenium, Postman.",
        "мне нуженно срочно поэтом разрабочик с опытом работу не менее трех лет",
        "мне нужна вакансия бекент разрабочика на джава",
        "мне нужно 10 килограмм яблок",
        "мне нужен быкент разрабочик сопотом десять лет",
        "мне нужен фронтент разрабочик с опытом один год",
        "Ищу грузчиков для работы на складе",
        "Требуется бухгалтер со знанием 1С",
        "Резюме: Python-разработчик. Навыки: Python, Django."  # Нет опыта работы
    ]

    try:
        token = get_oauth_token(GIGACHAT_API_KEY)
        for example in examples:
            print(f"\nТекст: {example}")
            result = process_text(example, token)
            print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")