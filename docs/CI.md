# Intégration continue (CI) — GitHub Actions

Pipeline CI pour **RecruitSaas / TalentFlow** : tests unitaires, tests API, lint frontend, coverage, intégration multi-services et build Docker.

---

## 1. Fichier de workflow

**Emplacement :** `.github/workflows/ci.yml`

**Déclencheurs :** push / PR sur `main`

---

## 2. Jobs exécutés

| Job | Niveau | Action |
|-----|--------|--------|
| `build-backend` | Correct + Très bon | xUnit (unitaires + API + intégration) + **coverage** |
| `build-frontend` | Correct + Très bon | **ESLint** + `npm run build` |
| `build-ai` | Correct + Excellent | pytest (validation + sanity) + **coverage** |
| `integration` | Excellent | **docker compose** postgres + backend + IA |
| `docker-build` | Correct | `docker build` × 3 |

---

## 3. Tests backend (`RecruitSaas-backend/Recrutement-api.Tests/`)

### Tests unitaires
| Fichier | Ce qui est testé |
|---------|------------------|
| `JwtServiceTests` | Génération JWT, claims, expiration |
| `AuthServicePasswordTests` | Hash / verify (Identity + BCrypt) |
| `CvFileTypeDetectorTests` | Détection PDF/PNG/Cloudinary |
| `LinkGeneratorServiceTests` | Génération lien offre publique |
| `ExternalAuthExtensionsTests` | Providers OAuth configurés |

### Tests API / intégration (InMemory DB)
| Fichier | Ce qui est testé |
|---------|------------------|
| `HealthEndpointTests` | `GET /health` |
| `AuthApiTests` | register, login, providers, `/me` |
| `ProtectedEndpointTests` | endpoints protégés → 401 sans token |

**Coverage :** Coverlet → artefact `coverage-backend` (Cobertura + OpenCover)

---

## 4. Tests service IA (`recruit-ai-service/tests/`)

| Fichier | Tests |
|---------|-------|
| `test_health.py` | `GET /` |
| `test_openapi.py` | `/openapi.json`, `/docs` |
| `test_api_validation.py` | validation 400, evaluate-answer sans LLM, summarize fallback |
| `test_sanity_helpers.py` | `stable_seed`, `clean_cv_text`, `parse_json_array` |

**18 tests** — sans modèle NER ni clé Groq réelle.

**Coverage :** pytest-cov → artefact `coverage-ai` (`coverage.xml`)

---

## 5. Frontend

```bash
npm ci
npm run lint    # ESLint (eslint.config.js)
npm run build
```

`package-lock.json` doit être versionné.

---

## 6. Intégration multi-services

**Fichiers :** `docker-compose.ci.yml`, `.github/scripts/ci-integration.sh`

1. Démarre PostgreSQL + backend + service IA
2. Attend les healthchecks
3. Vérifie `/health` (backend) et `/` (IA) depuis l'hôte
4. Vérifie la connectivité **backend ↔ IA** sur le réseau Docker

---

## 7. Schéma du pipeline

```
Push / PR sur main
        │
        ├── build-backend   ──┐
        ├── build-frontend  ──┼──▶ integration ──▶ docker-build
        └── build-ai        ──┘
```

---

## 8. Lancer en local

```powershell
# Backend + coverage
cd RecruitSaas-backend/Recrutement-api.Tests
$env:APPLY_MIGRATIONS="false"
dotnet test -c Release

# Service IA + coverage
cd recruit-ai-service
pip install -r requirements.txt -r requirements-dev.txt
$env:GROQ_API_KEY="test-key-for-ci"
pytest tests/ -v --cov=. --cov-report=term-missing

# Frontend lint + build
cd RecruitSaas-frontend
npm ci
npm run lint
npm run build

# Intégration multi-services
bash .github/scripts/ci-integration.sh
```

---

## 9. Grille PFE

| Niveau | Critères | Statut |
|--------|----------|--------|
| **Correct** | Tests backend, Python, build frontend, docker build | ✅ |
| **Très bon** | Tests API, lint frontend, intégration | ✅ |
| **Excellent** | Sanity checks IA, coverage, multi-services | ✅ |

**Non inclus (optionnel) :** Vitest frontend, tests E2E Playwright, push GHCR.

---

*Voir aussi : [DOCKER.md](./DOCKER.md)*
