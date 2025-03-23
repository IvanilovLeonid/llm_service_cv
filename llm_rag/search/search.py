import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess(text: str) -> str:
    return text.lower().strip()


def simple_resume_search(vacancy_json: dict, resumes_api_url: str = "http://localhost:8000/resumes/"):
    # 1. Получаем direction и skills из вакансии
    direction = preprocess(vacancy_json.get("direction", ""))
    skills_raw = vacancy_json.get("skills", "")
    skills_list = [preprocess(skill) for skill in skills_raw.split(",") if skill.strip()]
    combined_query = f"{direction} {' '.join(skills_list)}"

    # 2. Получаем все резюме из базы
    try:
        response = requests.get(resumes_api_url)
        response.raise_for_status()
        resumes = response.json()
    except Exception as e:
        print(f"❌ Ошибка при получении резюме: {e}")
        return []

    # 3. Подготовка данных для сравнения
    resume_texts = []
    resume_data = []

    for resume in resumes:
        r_direction = preprocess(resume.get("direction", ""))
        r_skills = resume.get("skills", "")
        r_skills_list = [preprocess(s) for s in r_skills.split(",") if s.strip()]
        combined_text = f"{r_direction} {' '.join(r_skills_list)}"
        resume_texts.append(combined_text)
        resume_data.append(resume)

    # 4. Векторизация и сравнение
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([combined_query] + resume_texts)
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    # 5. Сортировка результатов
    sorted_results = sorted(zip(resume_data, similarities), key=lambda x: x[1], reverse=True)

    return sorted_results  # список кортежей (резюме, схожесть)


vacancy = {
    "direction": "Backend Developer",
    "skills": "Go, Echo, PostgreSQL, gRPC, Docker, Git, CI/CD",
    "tasks": "Разработка микросервисов, работа с gRPC, настройка CI/CD"
}

if __name__ == "__main__":
    results = simple_resume_search(vacancy)

    for i, (resume, score) in enumerate(results[:5], 1):
        print(f"{i}. {resume['full_name']} — Похожесть: {score:.3f} {resume['pdf_filename']}")
        print(resume['skills'])
