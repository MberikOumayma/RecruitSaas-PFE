import pytest

LONG_CV = (
    "Jean Dupont — Développeur Full Stack avec plus de cinq ans d'expérience "
    "en JavaScript, Vue.js, ASP.NET Core et PostgreSQL."
)


@pytest.mark.parametrize(
    "path",
    [
        "/ai/score",
        "/ai/summarize",
        "/ai/extract-skills",
        "/ai/extract-experience",
        "/ai/extract-certifications",
        "/ai/extract-companies",
    ],
)
def test_endpoints_reject_short_cv_text(client, path):
    response = client.post(path, json={"texteExtrait": "too short"})
    assert response.status_code == 400
    assert "too short" in response.json()["detail"].lower()


def test_rank_candidates_rejects_empty_list(client):
    response = client.post(
        "/ai/rank-candidates",
        json={
            "titreOffre": "Développeur Full Stack",
            "description": "Vue + .NET",
            "candidates": [],
        },
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_summarize_requires_skills_or_experience(client):
    response = client.post(
        "/ai/summarize",
        json={"texteExtrait": LONG_CV},
    )
    assert response.status_code == 400
    assert "skills or experience" in response.json()["detail"].lower()


def test_generate_report_requires_questions(client):
    response = client.post(
        "/ai/generate-report",
        json={
            "titreOffre": "Dev",
            "nomCandidat": "Jean",
            "questions": [],
        },
    )
    assert response.status_code == 400


def test_extract_cv_text_rejects_empty_upload(client):
    response = client.post(
        "/ai/extract-cv-text",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_evaluate_answer_skips_llm_for_empty_response(client):
    response = client.post(
        "/ai/evaluate-answer",
        json={
            "question": "Parlez-moi de vous.",
            "reponse": "",
            "titreOffre": "Dev",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 0
    assert data["points_forts"] == []


def test_summarize_with_provided_skills_uses_fallback_without_groq(client):
    response = client.post(
        "/ai/summarize",
        json={
            "texteExtrait": LONG_CV,
            "skills": ["Vue.js", "ASP.NET Core", "PostgreSQL"],
            "experiences": [
                {
                    "role": "Développeur Full Stack",
                    "entreprise": "Acme",
                    "years": "2020-2024",
                }
            ],
            "titreOffre": "Développeur Full Stack",
            "description": "Vue.js et .NET",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["summary"]) >= 30
