import requests
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Предобработка текста: нижний регистр и удаление лишнего
def preprocess(text: str) -> str:
    return text.strip()


# Кэш вакансий, чтобы не загружать каждый раз
_cached_vacancies = None


def fetch_vacancies_once(api_url: str) -> List[Dict]:
    global _cached_vacancies
    if _cached_vacancies is not None:
        return _cached_vacancies

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            _cached_vacancies = response.json()
        else:
            print(f"❌ Ошибка загрузки вакансий: {response.status_code} - {response.text}")
            _cached_vacancies = []
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        _cached_vacancies = []

    return _cached_vacancies


def vector_match_single(item: str, corpus: List[str], threshold: float = 0.1) -> str:
    """
    Возвращает наиболее близкий элемент из `corpus` по косинусной близости, иначе — оригинал.
    """
    vectorizer = TfidfVectorizer().fit(corpus + [item])
    item_vec = vectorizer.transform([item])
    corpus_vec = vectorizer.transform(corpus)

    similarities = cosine_similarity(item_vec, corpus_vec)[0]
    max_idx = np.argmax(similarities)

    # if similarities[max_idx] >= 0.01:
    return corpus[max_idx]
    # return item


def process_resume_with_matching(resume_json: Dict, api_url: str) -> Dict:
    vacancies = fetch_vacancies_once(api_url)

    if not vacancies:
        print("⚠️ Вакансий нет, возвращаю резюме без изменений.")
        return resume_json

    # --- Direction Matching ---
    all_directions = list({preprocess(v.get("direction", "")) for v in vacancies if v.get("direction")})
    original_direction = preprocess(resume_json.get("direction", ""))
    matched_direction = vector_match_single(original_direction, all_directions) if all_directions else resume_json.get("direction", "")

    # --- Skill Matching ---
    all_vac_skills = []
    for vac in vacancies:
        raw = vac.get("skills", "")
        skills = [preprocess(skill) for skill in raw.split(",") if skill.strip()]
        all_vac_skills.extend(skills)

    all_vac_skills = list(set(all_vac_skills))  # Уникальные навыки
    resume_skills = [
        preprocess(skill) for skill in resume_json.get("skills", "").split(",") if skill.strip()
    ]

    matched_skills = []
    for skill in resume_skills:
        if all_vac_skills:
            matched = vector_match_single(skill, all_vac_skills)
            # Добавляем только если есть хорошее совпадение, иначе оставляем оригинал
            if matched and matched != "":
                matched_skills.append(matched)
            else:
                matched_skills.append(skill)
        else:
            matched_skills.append(skill)

    # --- Формируем новый JSON ---
    return {
        "full_name": resume_json.get("full_name"),
        "direction": matched_direction,
        "skills": ", ".join(matched_skills),
        "experience": resume_json.get("experience")
    }

