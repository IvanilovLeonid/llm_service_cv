import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import json

# URL API с резюме
RESUMES_API_URL = "http://localhost:8000/resumes/"

# ---------- СИНОНИМЫ НАВЫКОВ (оставим как есть) ----------
SKILL_SYNONYMS = {
    # ... [оставим как в твоём коде]
}


def load_resumes_from_api(api_url: str = RESUMES_API_URL):
    """Загрузка резюме с API вместо CSV"""
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # если статус не 2xx — бросит исключение
        data = response.json()

        if not isinstance(data, list):
            raise ValueError("Ответ от API должен быть списком резюме")

        return data

    except Exception as e:
        print(f"❌ Ошибка при загрузке резюме с API: {e}")
        return []


def normalize_skill(skill: str) -> str:
    skill = skill.lower().strip()
    for base, variants in SKILL_SYNONYMS.items():
        if skill in variants or skill == base:
            return base
    return skill


def preprocess(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    return ' '.join(text.split())


def calculate_skill_match(vacancy_skills, candidate_skills):
    matched = 0
    norm_vacancy_skills = {normalize_skill(s) for s in vacancy_skills}
    norm_candidate_skills = {normalize_skill(s) for s in candidate_skills}
    return len(norm_vacancy_skills & norm_candidate_skills) / len(norm_vacancy_skills) if norm_vacancy_skills else 0


def enhanced_resume_search(vacancy: dict, resumes_data: list) -> List[Dict[str, Any]]:
    direction = preprocess(vacancy.get("direction", ""))
    skills_raw = vacancy.get("skills", "")
    vacancy_skills = [preprocess(skill) for skill in skills_raw.split(",") if skill.strip()]

    results = []
    for resume in resumes_data:
        r_direction = preprocess(resume.get("direction", ""))
        r_skills = [preprocess(skill) for skill in resume.get("skills", "").split(",") if skill.strip()]

        direction_sim = 1.0 if direction in r_direction or r_direction in direction else 0.0
        skill_match_score = calculate_skill_match(vacancy_skills, r_skills)
        experience_bonus = 0.1 if any(word in resume.get("experience", "").lower()
                                      for word in ["год", "лет", "experience"]) else 0.0

        final_score = min(1.0, (0.5 * direction_sim +
                                0.4 * skill_match_score +
                                0.1 * experience_bonus) * 1.15)

        result = {
            "resume": {
                "id": resume.get("id", 0),
                "full_name": resume.get("full_name", ""),
                "direction": resume.get("direction", ""),
                "skills": resume.get("skills", ""),
                "experience": resume.get("experience", "Не указан"),
                "pdf_filename": resume.get("pdf_filename", "")
            },
            "similarity": round(final_score, 4)
        }

        results.append(result)

    return sorted(results, key=lambda x: x["similarity"], reverse=True)


if __name__ == "__main__":
    vacancy = {
        "direction": "Инженер микро сервисной архитектуры",
        "skills": "Golang, Kafka, gRPC, Kubernetes",
        "tasks": "Создание и сопровождение микросервисов, взаимодействие через gRPC, работа с event-очередями"
    }

    resumes = load_resumes_from_api()

    if not resumes:
        print("Не удалось загрузить резюме с API.")
    else:
        results = enhanced_resume_search(vacancy, resumes)
        filtered_results = [res for res in results if res["similarity"] >= 0.5]
        output = json.dumps(filtered_results, ensure_ascii=False, indent=2)
        print(output)
