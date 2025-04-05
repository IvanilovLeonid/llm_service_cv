import re
import requests
import uuid
from time import sleep
# Отключаем предупреждения SSL
requests.packages.urllib3.disable_warnings()

# Константы для API GigaChat
GIGACHAT_API_KEY = "M2ZhMjE1ZmUtYTM5Yi00OTNkLTllMGUtYmEzZmJmNmFmZDU1OmE4OGJhNGY1LWI5OTgtNDFmOC04OWRjLWNjNzkyMmE4MzYyNA=="
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

REPLACEMENTS = {
    # Направления
    r'\b(бэкенд|бекенд|бекендер|бек|бэк|backend)\w*\b': 'Backend Developer',
    r'\b(фронтент|фронтенд|фронтендер|фронд|фронт|frontend|фронтенд-разработчик)\w*\b': 'Frontend Developer',
    r'\b(qa|кьюей|тестировщик|qa-инженер|тестер)\w*\b': 'QA Engineer',
    r'\b(дата\s*аналитик|data\s*analyst)\w*\b': 'Data Analyst',
    r'\b(питон|пайтон|python|python-разработчик)\w*\b': 'Python Developer',
    r'\b(девопс|devops|devops-специалист)\w*\b': 'DevOps Specialist',
    r'\b(машинное\s+обучение|машинка|ml|machine\s+learning)\w*\b': 'ML-engineer',
    r'\b(микросервис|микро\s*сервис|микросервисная\s*архитектура)\w*\b': 'Microservices Architecture Engineer',
    r'\b(мобильный\s*разработчик|ios\s*разработчик)\w*\b': 'Mobile Developer (iOS)',
    r'\b(искуственный\s+интеллект|ии|ai)\w*\b': 'Artificial Intelligence Specialist',

    # Навыки
    r'\b(скл|эскюэл|sql)\w*\b': 'SQL',
    r'\b(джава|джавист|java|javascript)\w*\b': 'JavaScript',
    r'\b(реакт|react)\w*\b': 'React',
    r'\b(нод|node\.js|nodejs)\w*\b': 'Node.js',
    r'\b(докер|докер компоуз|докер композ|docker|docker-compose|docker compose)\w*\b': 'Docker',
    r'\b(кубернетис|kubernetes|k8s)\w*\b': 'Kubernetes',
    r'\b(гит|git)\w*\b': 'Git',
    r'\b(рест|rest\s*api)\w*\b': 'REST API',
    r'\b(графкл|graphql)\w*\b': 'GraphQL',

    # Уровень опыта
    r'\b(джун|джуниор|junior)\w*\b': 'Junior',
    r'\b(мидл|мидл-плюс|middle)\w*\b': 'Middle',
    r'\b(сеньор|синьор|senior)\w*\b': 'Senior',
    r'\b(тимлид|team\s*lead)\w*\b': 'Team Lead',
}

DIRECTIONS = {
    # Направления
    r'\b(бэкенд|бекенд|бекендер|бек|бэк|backend)\w*\b': 'Backend Developer',
    r'\b(фронтент|фронтенд|фронтендер|фронд|фронт|frontend)\w*\b': 'Frontend Developer',
    r'\b(qa|кьюей|тестировщик|qa-инженер|тестер)\w*\b': 'QA Engineer',
    r'\b(дата\s*аналитик|data\s*analyst)\w*\b': 'Data Analyst',
    r'\b(питон|пайтон|python|Python|python-разработчик)\w*\b': 'Python Developer',
    r'\b(девопс|devops|devops-специалист)\w*\b': 'DevOps Specialist',
    r'\b(машинное\s+обучение|машинка|ml|machine\s+learning)\w*\b': 'ML-engineer',
    r'\b(микросервис|микро\s*сервис|микросервисная\s*архитектура)\w*\b': 'Microservices Architecture Engineer',
    r'\b(мобильный\s*разработчик|ios\s*разработчик)\w*\b': 'Mobile Developer (iOS)',
    r'\b(искуственный\s+интеллект|ии|ai)\w*\b': 'Artificial Intelligence Specialist',
}
SKILLS = {
    # Основные языки программирования
    r'\b(джава|джавист|java|javascript|js)\w*\b': 'JavaScript',
    r'\b(python|питон|пайтон)\w*\b': 'Python',
    r'\b(go|golang)\w*\b': 'Golang',
    r'\b(ruby|руби)\w*\b': 'Ruby',
    r'\b(c sharp|c#)\w*\b': 'C#',
    r'\b(c plus plus|c\+\+)\w*\b': 'C++',
    r'\b(kotlin|котелин)\w*\b': 'Kotlin',
    r'\b(swift|свифт)\w*\b': 'Swift',
    r'\b(scala|скала)\w*\b': 'Scala',
    r'\b(php|пых|пхп)\w*\b': 'PHP',

    # Фронтенд
    r'\b(реакт|react)\w*\b': 'React',
    r'\b(vue|вью)\w*\b': 'Vue.js',
    r'\b(vuex|вьюкс)\w*\b': 'Vuex',
    r'\b(angular|ангуляр)\w*\b': 'Angular',
    r'\b(next\.js|nextjs|некст)\w*\b': 'Next.js',
    r'\b(typescript|тс)\w*\b': 'TypeScript',
    r'\b(redux|редукс)\w*\b': 'Redux',
    r'\b(redux toolkit)\w*\b': 'Redux Toolkit',
    r'\b(rxjs)\w*\b': 'RxJS',
    r'\b(tailwind|тейлвинд)\w*\b': 'Tailwind CSS',
    r'\b(pwa)\w*\b': 'PWA',
    r'\b(ssr)\w*\b': 'SSR',
    r'\b(vite|вайт)\w*\b': 'Vite',

    # Бэкенд
    r'\b(нод|node\.js|nodejs)\w*\b': 'Node.js',
    r'\b(express|экспресс)\w*\b': 'Express',
    r'\b(django|джанго)\w*\b': 'Django',
    r'\b(flask|фляск)\w*\b': 'Flask',
    r'\b(fastapi)\w*\b': 'FastAPI',
    r'\b(spring boot)\w*\b': 'Spring Boot',
    r'\b(laravel|ларавел)\w*\b': 'Laravel',
    r'\b(ruby on rails|rails)\w*\b': 'Ruby on Rails',
    r'\b(gin|джин)\w*\b': 'Gin',
    r'\b(echo|эхо)\w*\b': 'Echo',
    r'\b(\.net|dotnet)\w*\b': '.NET',

    # Базы данных
    r'\b(скл|эскюэл|sql)\w*\b': 'SQL',
    r'\b(postgres|postgresql|постгрес)\w*\b': 'PostgreSQL',
    r'\b(mysql|майскл)\w*\b': 'MySQL',
    r'\b(mongodb|монго)\w*\b': 'MongoDB',
    r'\b(redis|редис)\w*\b': 'Redis',
    r'\b(sql server)\w*\b': 'SQL Server',
    r'\b(oracle|оракл)\w*\b': 'Oracle',
    r'\b(sqlalchemy)\w*\b': 'SQLAlchemy',

    # DevOps и инфраструктура
    r'\b(докер|докер компоуз|докер композ|docker|docker-compose)\w*\b': 'Docker',
    r'\b(кубернетис|kubernetes|k8s)\w*\b': 'Kubernetes',
    r'\b(ci cd|ci/cd)\w*\b': 'CI/CD',
    r'\b(terraform|терраформ)\w*\b': 'Terraform',
    r'\b(ansible|ансибл)\w*\b': 'Ansible',
    r'\b(nginx|энжинкс)\w*\b': 'Nginx',
    r'\b(jenkins|джеккинс)\w*\b': 'Jenkins',
    r'\b(prometheus|прометеус)\w*\b': 'Prometheus',
    r'\b(aws)\w*\b': 'AWS',
    r'\b(vpn)\w*\b': 'VPN',

    # Тестирование
    r'\b(selenium|селениум)\w*\b': 'Selenium',
    r'\b(jest|джест)\w*\b': 'Jest',
    r'\b(cypress|сайпресс)\w*\b': 'Cypress',
    r'\b(jmeter|джметер)\w*\b': 'JMeter',
    r'\b(k6)\w*\b': 'k6',
    r'\b(postman|постман)\w*\b': 'Postman',

    # Аналитика и BI
    r'\b(pandas|пандас)\w*\b': 'pandas',
    r'\b(power bi|powerbi)\w*\b': 'Power BI',
    r'\b(tableau|табло)\w*\b': 'Tableau',
    r'\b(etl)\w*\b': 'ETL',
    r'\b(hadoop|хадуп)\w*\b': 'Hadoop',
    r'\b(spark|спарк)\w*\b': 'Spark',
    r'\b(hive|хайв)\w*\b': 'Hive',

    # Мобильная разработка
    r'\b(android studio)\w*\b': 'Android Studio',
    r'\b(jetpack)\w*\b': 'Jetpack',
    r'\b(coredata)\w*\b': 'CoreData',
    r'\b(uikit)\w*\b': 'UIKit',

    # Другие технологии
    r'\b(graphql|графкл)\w*\b': 'GraphQL',
    r'\b(websockets|вебсокеты)\w*\b': 'WebSockets',
    r'\b(grpc)\w*\b': 'gRPC',
    r'\b(kafka|кафка)\w*\b': 'Kafka',
    r'\b(rabbitmq|рэббит)\w*\b': 'RabbitMQ',
    r'\b(celery|селери)\w*\b': 'Celery',
    r'\b(sidekiq|сайдкик)\w*\b': 'Sidekiq',

    # Инструменты разработки
    r'\b(гит|git)\w*\b': 'Git',
    r'\b(рест|rest\s*api)\w*\b': 'REST API',
    r'\b(jira|джира)\w*\b': 'Jira',
    r'\b(confluence|конфлюенс)\w*\b': 'Confluence',
    r'\b(figma|фигма)\w*\b': 'Figma',
    r'\b(sketch|скетч)\w*\b': 'Sketch',
    r'\b(storybook|сторибук)\w*\b': 'Storybook',
    r'\b(webpack|вебпак)\w*\b': 'Webpack',
    r'\b(markdown|маркдаун)\w*\b': 'Markdown',

    # Безопасность
    r'\b(pentest|пентест)\w*\b': 'Pentest',
    r'\b(owasp)\w*\b': 'OWASP',

    # Софт-скиллы
    r'\b(коммуникации)\w*\b': 'Коммуникации',
    r'\b(управление командой)\w*\b': 'Управление командой',
    r'\b(архитектура)\w*\b': 'Архитектура ПО',
    r'\b(бизнес процессы)\w*\b': 'Бизнес-процессы',

    # Специализированные технологии
    r'\b(tensorflow|тензорфлоу)\w*\b': 'TensorFlow',
    r'\b(pytorch|пайторч)\w*\b': 'PyTorch',
    r'\b(mlflow)\w*\b': 'MLFlow',
    r'\b(gpt)\w*\b': 'GPT',
    r'\b(llm)\w*\b': 'LLM',
    r'\b(langchain)\w*\b': 'LangChain',
    r'\b(ros)\w*\b': 'ROS',
    r'\b(rtos)\w*\b': 'RTOS',
    r'\b(3d графика|3d graphics)\w*\b': '3D-графика',
    r'\b(unity|юнити)\w*\b': 'Unity',
}
EXPERIENCE_LEVELS = {
    # Уровень опыта
    r'\b(джун|джуниор|junior)\w*\b': 'Junior',
    r'\b(мидл|мидл-плюс|middle)\w*\b': 'Middle',
    r'\b(сеньор|синьор|senior)\w*\b': 'Senior',
    r'\b(тимлид|team\s*lead)\w*\b': 'Team Lead',
}

TASKS = {
    r'\b(разработка\s+backend-сервисов)\w*\b': 'Backend Development',
    r'\b(тестирование\s+приложений)\w*\b': 'Application Testing',
    # ... остальные задачи ...
}

THEMES = {
    "резюме": ["направление", "навыки", "опыт работы"],  # Всегда показываем эти поля для вакансий
    "другое": []  # Для некорректных запросов
}


KEY_TRANSLATION = {
    "направление": "direction",
    "навыки": "skills",
    "опыт работы": "experience",
    "задачи": "tasks"
}

def levenshtein_distance(s1, s2):
    """Вычисляет расстояние Левенштейна между двумя строками."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_percent(s1, s2):
    """Вычисляет процент совпадения между двумя строками."""
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 100  # Если обе строки пустые, считаем их одинаковыми
    return (1 - distance / max_len) * 100


def extract_keys_from_regex(pattern):
    """Извлекает ключи из регулярного выражения."""
    match = re.match(r'\\b\((.*?)\)\\w*\*\?*\\b', pattern)
    if match:
        return [k.strip() for k in match.group(1).split('|')]
    return []


def replace_using_dict(input_phrase, replacements, threshold=80):
    """Заменяет слова в фразе на основе словаря и процента совпадения."""
    words = re.findall(r'\w+[\w-]*\w+|\w+', input_phrase.lower())
    for i in range(len(words)):
        word = words[i]
        for pattern, replacement in replacements.items():
            keys = extract_keys_from_regex(pattern)
            for key in keys:
                if similarity_percent(word, key.lower()) >= threshold:
                    words[i] = replacement
                    break
    return ' '.join(words)


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


import time


def call_gigachat_api(prompt, token):
    """Отправляет запрос к API GigaChat и возвращает очищенный ответ."""
    # Добавляем задержку перед запросом
    time.sleep(1)  # 1 секунда задержки

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
        if response.status_code == 429:
            # Если превышен лимит, ждем дольше и пробуем снова
            time.sleep(5)  # Увеличиваем задержку до 5 секунд
            return call_gigachat_api(prompt, token)  # Рекурсивный вызов
        raise Exception(f"Ошибка HTTP: {response.status_code}, {response.text}") from e
    except Exception as e:
        raise Exception(f"Неизвестная ошибка: {str(e)}") from e


def determine_theme(text, token):
    """Строгое определение темы с использованием ключевых слов"""
    # Ключевые слова для поиска вакансий (поиск сотрудников)
    vacancy_keywords = {'требуется', 'нужен', 'нужна', 'ищем', 'вакансия', 'срочно', 'ищется', 'подбор', 'найти'}

    # Ключевые слова для поиска работы
    job_search_keywords = {'ищу работу', 'ищу позицию', 'рассматриваю предложения', 'соискатель', 'ищу вакансию',
                           'хочу работать'}

    text_lower = text.lower()

    # Проверяем сначала по ключевым словам
    has_vacancy = any(word in text_lower for word in vacancy_keywords)
    has_job_search = any(word in text_lower for word in job_search_keywords)

    if has_vacancy and not has_job_search:
        return 'резюме'
    elif has_job_search and not has_vacancy:
        return 'другое'

    # Если не определили по ключевым словам, уточняем у модели
    prompt = f"""Определи тип запроса. Варианты:
    1. "резюме" - если это запрос на поиск сотрудников, чтобы был показан список подходящих кандидатов(резюме)
    2. "другое" - если это иной запрос

    Примеры "резюме":
    - Нужен программист Python и Django
    - Ищем фронтенд-разработчика
    - Требуется DevOps инженер с опытом 3 года

    Примеры "другое":
    - Какая сегодня погода
    - Сколько стоит машина

    Текст: "{text}"
    Ответ (только ОДНО слово резюме или другое):"""

    response = call_gigachat_api(prompt, token).strip().lower()
    return response if response in ['резюме', 'другое'] else 'другое'


def check_it_theme(text, token):
    """Проверяет принадлежность текста к IT-программированию."""
    # Быстрая проверка по ключевым словам без обращения к API
    it_keywords = {'it', 'айти', 'программист', 'разработчик', 'developer',
                   'код', 'программа', 'алгоритм', 'база данных', 'backend',
                   'frontend', 'devops', 'qa', 'тестировщик', 'api', 'фреймворк',
                   'язык программирования', 'python', 'java', 'javascript', 'sql'}

    text_lower = text.lower()
    if any(keyword in text_lower for keyword in it_keywords):
        return True

    # Если по ключевым словам не определили, уточняем у API
    prompt = f"""
    Относится ли этот текст к сфере IT-программирования или смежным технологиям?
    Ответь только 'да' или 'нет' без пояснений.
    Текст: {text}
    Ответ:
    """
    response = call_gigachat_api(prompt, token)
    sleep(2)
    return response.strip().lower() == 'да'


def extract_keywords_with_gigachat(text, fields, token):
    """Улучшенное извлечение ключевых слов с гибридным подходом"""
    keywords = {}
    valid_directions = list(DIRECTIONS.values())
    valid_skills = list(SKILLS.values())

    for field in fields:
        if field == "направление":
            found_direction = None
            # Сначала ищем точное совпадение в тексте
            for direction in valid_directions:
                if re.search(r'\b' + re.escape(direction.lower()) + r'\b', text.lower()):
                    found_direction = direction
                    break

            # Если не нашли, проверяем по regex-шаблонам
            if not found_direction:
                for pattern, direction in DIRECTIONS.items():
                    if re.search(pattern, text, re.IGNORECASE):
                        found_direction = direction
                        break

            keywords[field] = [found_direction] if found_direction else ["Не указано"]

        elif field == "навыки":
            found_skills = []
            text_lower = text.lower()

            # Проверяем все навыки из словаря
            for pattern, skill in SKILLS.items():
                if re.search(pattern, text_lower):
                    found_skills.append(skill)

            # Проверяем английские названия навыков
            for skill in valid_skills:
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    if skill not in found_skills:
                        found_skills.append(skill)

            keywords[field] = list(set(found_skills)) if found_skills else ["Не указано"]

        elif field == "опыт работы":
            exp_match = re.search(r'(\d+)\s*(лет|года|год|year|years)', text, re.IGNORECASE)
            keywords[field] = [f"{exp_match.group(1)} {exp_match.group(2)}"] if exp_match else ["Не указано"]

    return keywords


def clean_response(text):
    """Агрессивная очистка ответов"""
    text = re.sub(r'^\W+', '', text)  # Удаляем начальные не-буквы
    text = re.sub(r'\W+$', '', text)  # Удаляем конечные не-буквы
    text = re.sub(r'исправленный текст:\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'ответ:\s*', '', text, flags=re.IGNORECASE)
    return text.strip()


def correct_text(text, token):
    """Коррекция текста без лишних слов"""
    prompt = f"""Исправь грамматику и технические термины в тексте, сохраняя исходный смысл.
    Используй только текст без пояснений и пометок.
    Текст: "{text}"
    Исправленный текст:"""

    response = call_gigachat_api(prompt, token)
    # Удаляем все, что может добавить модель
    response = re.sub(r'^исправленный текст:\s*', '', response, flags=re.IGNORECASE)
    return response.strip()


def preprocess_query(text):
    """Предварительная обработка запроса, удаление команд типа 'покажи мне'"""
    # Удаляем команды типа "покажи мне", "найди", "ищи" и т.д.
    text = re.sub(r'^(покажи\s+мне|найди|ищи|покажи|ищем|нужны?|требуются?)\s+', '', text, flags=re.IGNORECASE)
    return text.strip()


def extract_direction_from_query(text):
    """Пытается извлечь направление из запроса без обращения к API"""
    text_lower = text.lower()
    for pattern, direction in DIRECTIONS.items():
        if re.search(pattern, text_lower):
            return direction
    return None


def process_text(text, token):
    """Обновленная функция обработки текста"""
    original_text = text.strip()
    if not original_text or len(original_text) < 10:
        return {"error": "Текст некорректен. Проверьте ввод."}

    # 1. Предварительная обработка запроса
    preprocessed_text = preprocess_query(original_text)

    # 2. Замена опечаток
    context_corrected_text = replace_using_dict(preprocessed_text, REPLACEMENTS, threshold=80)

    # 3. Проверка IT-тематики
    if not check_it_theme(context_corrected_text, token):
        return {
            "original_text": original_text,
            "corrected_text": original_text,
            "flag": "не IT тематика",
            "corrected_keys": {},
            "message": "Данный вопрос не входит в мою компетенцию. Я могу помочь только с IT-тематикой."
        }

    # 4. Коррекция текста
    corrected_text = correct_text(context_corrected_text, token)

    # 5. Классификация
    theme = determine_theme(corrected_text, token)

    if theme == "другое":
        return {
            "original_text": original_text,
            "corrected_text": corrected_text,
            "flag": "некорректный запрос",
            "corrected_keys": {},
            "message": "Я могу помочь только с поиском IT-специалистов."
        }

    # 6. Извлечение ключевых слов
    fields = THEMES["резюме"]
    keywords = extract_keywords_with_gigachat(corrected_text, fields, token)

    # 7. Если направление не найдено, попробуем извлечь его вручную
    if "направление" not in keywords or keywords["направление"][0] == "Не указано":
        direction = extract_direction_from_query(corrected_text)
        if direction:
            keywords["направление"] = [direction]

    # 8. Перевод ключей
    translated_keywords = translate_keys(keywords, KEY_TRANSLATION)

    return {
        "original_text": original_text,
        "corrected_text": corrected_text,
        "flag": "резюме",
        "corrected_keys": translated_keywords
    }


# Примеры использования
if __name__ == "__main__":
    examples = [
        "покажи мне всех бекендеров которые занимаются разработкой веб-сайтов с помощью рест апи и го",
        "Ищу работу Python разработчиком"
    ]

    try:
        token = get_oauth_token(GIGACHAT_API_KEY)
        for example in examples:
            print(f"\nТекст: {example}")
            result = process_text(example, token)
            print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")