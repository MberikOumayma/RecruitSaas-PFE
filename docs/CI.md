# Documentation CI/CD & Tests — RecruitSaas / TalentFlow

Guide complet de l'intégration continue (CI), du déploiement continu (CD via GHCR) et de la suite de tests.

> **CD sans hébergement :** voir [CD.md](./CD.md) pour la publication automatique des images Docker sur GitHub Container Registry.

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture du pipeline](#2-architecture-du-pipeline)
3. [Déclencheurs et configuration globale](#3-déclencheurs-et-configuration-globale)
4. [Job 1 — Backend (.NET)](#4-job-1--backend-net)
5. [Job 2 — Frontend (Vue)](#5-job-2--frontend-vue)
6. [Job 3 — Service IA (Python)](#6-job-3--service-ia-python)
7. [Job 4 — Intégration multi-services](#7-job-4--intégration-multi-services)
8. [Job 5 — Build Docker](#8-job-5--build-docker)
9. [Artefacts et couverture de code](#9-artefacts-et-couverture-de-code)
10. [Commandes locales (référence rapide)](#10-commandes-locales-référence-rapide)
11. [Infrastructure de test backend](#11-infrastructure-de-test-backend)
12. [Dépannage](#12-dépannage)
13. [Grille de niveau PFE](#13-grille-de-niveau-pfe)
14. [Extensions possibles (non implémentées)](#14-extensions-possibles-non-implémentées)

---

## 1. Vue d'ensemble

Le projet RecruitSaas est une application **multi-services** :

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Frontend** | Vue 3 + Vite | Interface recruteur / candidat / expert |
| **Backend** | ASP.NET Core 10 | API REST, auth JWT, base PostgreSQL |
| **Service IA** | FastAPI + Python 3.12 | Scoring CV, NER, résumés, détection fraude |

La CI vérifie automatiquement, à chaque push ou pull request sur `main` :

- Compilation et **21 tests** backend (unitaires + API)
- **Lint ESLint** et build production du frontend
- **18 tests** Python sur le service IA (validation + sanity checks)
- Démarrage **Docker Compose** (PostgreSQL + backend + IA) et smoke tests réseau
- Construction des **3 images Docker**

**Fichier principal :** `.github/workflows/ci.yml`

**Durée typique en CI :** ~8 minutes (tous les jobs au vert).

---

## 2. Architecture du pipeline

```
Push / PR sur main
        │
        ├──────────────────────────────────────────┐
        │                                          │
        ▼                    ▼                     ▼
 build-backend         build-frontend          build-ai
 (.NET 10, xUnit)      (Node 20, ESLint)      (Python 3.12, pytest)
   21 tests               lint + build           18 tests
   + coverage             (pas de tests          + coverage
                           unitaires JS)
        │                    │                     │
        └────────────────────┼─────────────────────┘
                             ▼
                    integration
              (docker-compose.ci.yml)
           postgres + backend + ai-service
              smoke tests HTTP + réseau
                             │
                             ▼
                      docker-build
              build + push GHCR (main uniquement)
              ghcr.io/<owner>/recruitsaas-*
```

**Ordre d'exécution :**

1. Les 3 premiers jobs tournent **en parallèle**.
2. `integration` attend la réussite des 3.
3. `docker-build` attend la réussite de `integration`.

**Concurrence :** si un nouveau push arrive sur la même branche, le run en cours est annulé (`cancel-in-progress: true`).

---

## 3. Déclencheurs et configuration globale

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

| Élément | Valeur |
|---------|--------|
| Branche cible | `main` uniquement |
| Runners | `ubuntu-latest` |
| Annulation | Oui, en cas de push concurrent |

---

## 4. Job 1 — Backend (.NET)

### 4.1 Configuration CI

| Paramètre | Valeur |
|-----------|--------|
| Runner | `ubuntu-latest` |
| SDK | .NET 10.0.x |
| Projet de tests | `RecruitSaas-backend/Recrutement-api.Tests/` |
| Framework de test | xUnit 2.9 |
| Base de données (tests) | SQLite en mémoire (environnement `Testing`) |
| Couverture | Coverlet → Cobertura + OpenCover |

**Commande exécutée en CI :**

```bash
cd RecruitSaas-backend/Recrutement-api.Tests
export APPLY_MIGRATIONS=false
dotnet test -c Release --verbosity normal
```

### 4.2 Structure du projet de tests

```
RecruitSaas-backend/Recrutement-api.Tests/
├── Recrutement-api.Tests.csproj    # coverlet, xUnit, Mvc.Testing, SQLite
├── RecruitSaasApiFactory.cs        # WebApplicationFactory + SQLite partagé
├── IntegrationTestCollection.cs  # Collection xUnit partagée
├── JwtServiceTests.cs
├── AuthServicePasswordTests.cs
├── CvFileTypeDetectorTests.cs
├── LinkGeneratorServiceTests.cs
├── ExternalAuthExtensionsTests.cs
├── HealthEndpointTests.cs
├── AuthApiTests.cs
└── ProtectedEndpointTests.cs
```

### 4.3 Tests unitaires (13 tests)

Ces tests n'ont **pas besoin** de démarrer l'API HTTP. Ils testent des services ou helpers isolés.

#### `JwtServiceTests.cs` (2 tests)

| Test | Description |
|------|-------------|
| `GenerateToken_ContainsExpectedClaims` | Vérifie que le JWT contient `userId`, `role`, `tenantId`, issuer et audience |
| `GenerateToken_ExpiresInAboutThreeHours` | Vérifie que le token expire entre 2,5 h et 3,5 h |

#### `AuthServicePasswordTests.cs` (2 tests)

| Test | Description |
|------|-------------|
| `HashPassword_AndVerifyPassword_RoundTripSucceeds` | Hash Identity + vérification mot de passe correct / incorrect |
| `VerifyPassword_AcceptsBcryptHash` | Compatibilité avec les hash BCrypt (experts) |

#### `CvFileTypeDetectorTests.cs` (4 tests)

| Test | Description |
|------|-------------|
| `DetectExtension_PdfMagicBytes_ReturnsPdf` | Détection PDF via magic bytes `%PDF` |
| `DetectExtension_PngMagicBytes_ReturnsPng` | Détection PNG via en-tête binaire |
| `DetectExtension_CloudinaryRawUrl_ReturnsPdf` | URL Cloudinary `/raw/upload/` → `.pdf` |
| `IsImageExtension_RecognizesCommonImageTypes` | `.jpg`, `.png` = image ; `.pdf` = non |

#### `LinkGeneratorServiceTests.cs` (1 test)

| Test | Description |
|------|-------------|
| `GenerateOfferLink_IncludesToken` | Lien public `http://localhost:5173/public/offres/{token}` |

#### `ExternalAuthExtensionsTests.cs` (4 tests)

| Test | Description |
|------|-------------|
| `IsProviderConfigured_ReturnsFalse_WhenSecretsMissing` | Google, Facebook, LinkedIn sans config → `false` |
| `IsProviderConfigured_ReturnsTrue_WhenGoogleConfigured` | Google avec ClientId + ClientSecret → `true` |

### 4.4 Tests API / intégration (8 tests)

Ces tests démarrent l'application ASP.NET Core via `WebApplicationFactory<Program>` avec une base SQLite en mémoire.

Toutes les classes utilisent la collection xUnit **`[Collection("Integration")]`** pour partager une seule factory et éviter les conflits de création de schéma.

#### `HealthEndpointTests.cs` (1 test)

| Test | Endpoint | Attendu |
|------|----------|---------|
| `GetHealth_ReturnsHealthyStatus` | `GET /health` | HTTP 200, corps contient « Healthy » |

#### `AuthApiTests.cs` (5 tests)

| Test | Scénario | Attendu |
|------|----------|---------|
| `GetExternalProviders_ReturnsOk` | `GET /api/auth/external/providers` | HTTP 200, JSON avec `providers` |
| `Login_WithInvalidCredentials_ReturnsUnauthorized` | Login email inconnu | HTTP 401 |
| `RegisterCandidate_ThenLogin_ReturnsToken` | Inscription candidat puis login | HTTP 200, token JWT, rôle `Candidat` |
| `RegisterCandidate_WithDuplicateEmail_ReturnsBadRequest` | Double inscription même email | 2e appel → HTTP 400 |
| `GetMe_WithValidToken_ReturnsCurrentUser` | Register + login + `GET /api/auth/me` avec Bearer | HTTP 200, email présent dans la réponse |

#### `ProtectedEndpointTests.cs` (2 tests)

| Test | Endpoint | Attendu |
|------|----------|---------|
| `GetMe_WithoutToken_ReturnsUnauthorized` | `GET /api/auth/me` sans header | HTTP 401 |
| `GetCandidatures_WithoutToken_ReturnsUnauthorized` | `GET /api/candidatures` sans token | HTTP 401 |

### 4.5 Couverture backend

Configurée dans `Recrutement-api.Tests.csproj` :

```xml
<CollectCoverage>true</CollectCoverage>
<CoverletOutputFormat>cobertura,opencover</CoverletOutputFormat>
<CoverletOutput>./coverage/</CoverletOutput>
```

Artefact GitHub : **`coverage-backend`** (dossier `coverage/`).

### 4.6 Commandes locales — Backend

**PowerShell (Windows) :**

```powershell
cd RecruitSaas-backend\Recrutement-api.Tests
$env:APPLY_MIGRATIONS = "false"
dotnet restore
dotnet test -c Release --verbosity normal
```

**Exécuter un seul fichier de tests :**

```powershell
dotnet test -c Release --filter "FullyQualifiedName~AuthApiTests"
```

**Avec rapport de couverture détaillé :**

```powershell
dotnet test -c Release --collect:"XPlat Code Coverage"
```

**Bash (Linux / macOS / WSL) :**

```bash
cd RecruitSaas-backend/Recrutement-api.Tests
export APPLY_MIGRATIONS=false
dotnet test -c Release --verbosity normal
```

---

## 5. Job 2 — Frontend (Vue)

### 5.1 Configuration CI

| Paramètre | Valeur |
|-----------|--------|
| Node.js | 20.x |
| Cache npm | `RecruitSaas-frontend/package-lock.json` |
| Lint | ESLint 9 (`eslint.config.js`) |
| Build | Vite (`npm run build`) |
| Variable build | `VITE_API_ORIGIN=http://localhost:5202` |

**Commandes exécutées en CI :**

```bash
cd RecruitSaas-frontend
npm ci
npm run lint
npm run build
```

### 5.2 ESLint

Fichier : `RecruitSaas-frontend/eslint.config.js`

| Règle | Niveau | Note |
|-------|--------|------|
| `no-unused-vars` | warn | Variables non utilisées |
| `no-empty` | warn | Blocs `catch` / `if` vides |
| `no-useless-escape` | warn | Échappements inutiles |
| `vue/no-unused-components` | off | Composants importés mais non rendus |
| `vue/no-reserved-keys` | off | Clés réservées Vue |
| `vue/multi-word-component-names` | off | Noms de composants à un mot autorisés |

Le script lint autorise jusqu'à **50 warnings** (`--max-warnings 50`) pour ne pas bloquer la CI sur du code legacy.

### 5.3 Ce qui est vérifié

| Vérification | Oui / Non |
|--------------|-----------|
| Syntaxe JS/Vue valide | ✅ |
| Build production Vite | ✅ |
| Tests unitaires Vitest | ❌ (non implémentés) |
| Tests E2E Playwright | ❌ (non implémentés) |

### 5.4 Prérequis

Le fichier **`package-lock.json`** doit être versionné dans Git (requis pour `npm ci` en CI).

### 5.5 Commandes locales — Frontend

**PowerShell :**

```powershell
cd RecruitSaas-frontend
npm ci
npm run lint
$env:VITE_API_ORIGIN = "http://localhost:5202"
npm run build
```

**Lint sur un fichier précis :**

```powershell
npx eslint src/views/auth/Login.vue
```

**Mode développement (hors CI) :**

```powershell
npm run dev
```

---

## 6. Job 3 — Service IA (Python)

### 6.1 Configuration CI

| Paramètre | Valeur |
|-----------|--------|
| Python | 3.12 |
| Framework | pytest + pytest-cov |
| Client HTTP | FastAPI `TestClient` |
| Clé Groq | `test-key-for-ci` (factice, pas d'appel LLM réel) |

**Commandes exécutées en CI :**

```bash
cd recruit-ai-service
pip install -r requirements.txt -r requirements-dev.txt
GROQ_API_KEY=test-key-for-ci pytest tests/ -v --cov=. --cov-report=xml --cov-report=term-missing
```

### 6.2 Structure des tests

```
recruit-ai-service/
├── pytest.ini
├── requirements-dev.txt      # pytest, pytest-cov, httpx
└── tests/
    ├── conftest.py           # fixture client + GROQ_API_KEY
    ├── test_health.py
    ├── test_openapi.py
    ├── test_api_validation.py
    └── test_sanity_helpers.py
```

### 6.3 Détail des 18 tests

#### `test_health.py` (1 test)

| Test | Description |
|------|-------------|
| `test_health_returns_ok` | `GET /` → 200, `status: ok`, champ `version` présent |

#### `test_openapi.py` (2 tests)

| Test | Description |
|------|-------------|
| `test_openapi_json_lists_core_routes` | Schéma OpenAPI contient `/ai/score`, `/ai/summarize`, `/ai/rank-candidates` |
| `test_docs_endpoint_returns_html` | `GET /docs` → 200, content-type HTML |

#### `test_api_validation.py` (12 tests)

| Test | Endpoint(s) | Attendu |
|------|-------------|---------|
| `test_endpoints_reject_short_cv_text` (×6) | `/ai/score`, `/ai/summarize`, `/ai/extract-skills`, `/ai/extract-experience`, `/ai/extract-certifications`, `/ai/extract-companies` | HTTP 400 si texte CV < seuil |
| `test_rank_candidates_rejects_empty_list` | `/ai/rank-candidates` | HTTP 400 si liste candidats vide |
| `test_summarize_requires_skills_or_experience` | `/ai/summarize` | HTTP 400 sans skills ni experiences |
| `test_generate_report_requires_questions` | `/ai/generate-report` | HTTP 400 si `questions: []` |
| `test_extract_cv_text_rejects_empty_upload` | `/ai/extract-cv-text` | HTTP 400 si fichier vide |
| `test_evaluate_answer_skips_llm_for_empty_response` | `/ai/evaluate-answer` | HTTP 200, score 0, sans appel LLM |
| `test_summarize_with_provided_skills_uses_fallback_without_groq` | `/ai/summarize` | HTTP 200, résumé ≥ 30 caractères (fallback local) |

> **Important :** aucun test ne charge le modèle NER spaCy ni n'appelle l'API Groq en production. Les tests restent rapides et fiables en CI.

#### `test_sanity_helpers.py` (3 tests)

| Test | Fonction testée | Description |
|------|-----------------|-------------|
| `test_stable_seed_is_deterministic` | `stable_seed()` | Même entrée → même seed ; entrées différentes → seeds différents |
| `test_clean_cv_text_adds_spaces_between_words_and_digits` | `clean_cv_text()` | Normalisation texte CV (`VueJS2024` → espaces ajoutés) |
| `test_parse_json_array_extracts_array_from_markdown` | `parse_json_array()` | Extraction JSON depuis bloc markdown ```json |

### 6.4 Couverture IA

Configurée dans `pytest.ini` :

```ini
[coverage:run]
source = .
omit = tests/*, models/*, __pycache__/*
```

Artefact GitHub : **`coverage-ai`** (`coverage.xml`).

### 6.5 Commandes locales — Service IA

**PowerShell :**

```powershell
cd recruit-ai-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
$env:GROQ_API_KEY = "test-key-for-ci"
pytest tests/ -v --cov=. --cov-report=term-missing
```

**Un seul fichier :**

```powershell
pytest tests/test_api_validation.py -v
```

**Bash :**

```bash
cd recruit-ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
export GROQ_API_KEY=test-key-for-ci
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 7. Job 4 — Intégration multi-services

### 7.1 Objectif

Vérifier que les **3 services** démarrent ensemble dans Docker et communiquent correctement, comme en production.

### 7.2 Fichiers impliqués

| Fichier | Rôle |
|---------|------|
| `docker-compose.ci.yml` | Stack minimale CI (postgres + backend + IA) |
| `.github/scripts/ci-integration.sh` | Script bash : up, smoke tests, down |

### 7.3 Services Docker Compose

| Service | Image / Build | Port hôte | Healthcheck |
|---------|---------------|-----------|-------------|
| `postgres` | `postgres:16-alpine` | (interne) | `pg_isready` |
| `ai-service` | Build `./recruit-ai-service` | 8000 | `GET /` |
| `backend` | Build `./RecruitSaas-backend/Recrutement-api` | 5202 | `GET /health` |

**Réseau Docker :** `recruitsaas-ci-net` (bridge)

**Variables backend clés :**

```env
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__DefaultConnection=Host=postgres;Port=5432;Database=RecruitmentDb_main;...
AiService__BaseUrl=http://ai-service:8000
APPLY_MIGRATIONS=true
```

### 7.4 Smoke tests exécutés

Le script `ci-integration.sh` effectue :

1. `docker compose up -d --build --wait --wait-timeout 900`
2. **Depuis l'hôte :**
   - `curl http://127.0.0.1:5202/health` → contient « healthy »
   - `curl http://127.0.0.1:8000/` → `"status":"ok"`
3. **Depuis le réseau Docker** (conteneur curl) :
   - `http://ai-service:8000/` → OK
   - `http://backend:5202/health` → OK
4. `docker compose down -v` (nettoyage automatique via `trap`)

### 7.5 Commandes locales — Intégration

**Prérequis :** Docker Desktop (Windows) ou Docker Engine (Linux), Docker Compose v2.

**Bash / Git Bash / WSL :**

```bash
bash .github/scripts/ci-integration.sh
```

**Équivalent manuel :**

```bash
# Démarrer la stack
docker compose -f docker-compose.ci.yml up -d --build --wait --wait-timeout 900

# Smoke tests
curl -fsS http://127.0.0.1:5202/health
curl -fsS http://127.0.0.1:8000/

# Tests réseau interne
docker run --rm --network recruitsaas-ci-net curlimages/curl:8.5.0 \
  -fsS http://backend:5202/health

# Arrêter et nettoyer
docker compose -f docker-compose.ci.yml down -v --remove-orphans
```

**PowerShell (smoke test simple après démarrage manuel) :**

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:5202/health -UseBasicParsing
Invoke-WebRequest -Uri http://127.0.0.1:8000/ -UseBasicParsing
```

---

## 8. Job 5 — Build Docker & push GHCR (CD)

### 8.1 Objectif

Confirmer que les **Dockerfiles** compilent, puis **publier** les images sur GitHub Container Registry (GHCR) à chaque push sur `main`.

Documentation détaillée : **[CD.md](./CD.md)**

### 8.2 Images

| Package GHCR | Contexte build |
|--------------|----------------|
| `ghcr.io/<owner>/recruitsaas-backend` | `./RecruitSaas-backend/Recrutement-api` |
| `ghcr.io/<owner>/recruitsaas-frontend` | `./RecruitSaas-frontend` |
| `ghcr.io/<owner>/recruitsaas-ai` | `./recruit-ai-service` |

Tags : `latest` et `<sha-commit>`.

### 8.3 Comportement

| Événement | Build | Push GHCR |
|-----------|-------|-----------|
| Push `main` | ✅ | ✅ |
| Pull Request | ✅ | ❌ |

### 8.4 Commandes locales — Docker (build seul)

```bash
# Backend
docker build -t recruitsaas-backend:local ./RecruitSaas-backend/Recrutement-api

# Frontend
docker build \
  --build-arg VITE_API_ORIGIN=http://localhost:5202 \
  -t recruitsaas-frontend:local \
  ./RecruitSaas-frontend

# Service IA
docker build -t recruitsaas-ai:local ./recruit-ai-service
```

**Pull depuis GHCR (après push sur main) :**

```bash
docker pull ghcr.io/<owner>/recruitsaas-backend:latest
```

---

## 9. Artefacts et couverture de code

| Artefact | Job source | Contenu | Condition upload |
|----------|------------|---------|------------------|
| `coverage-backend` | `build-backend` | `coverage/*.xml` (Cobertura, OpenCover) | `if: always()` |
| `coverage-ai` | `build-ai` | `coverage.xml` | `if: always()` |

**Télécharger depuis GitHub :** onglet Actions → run → section **Artifacts** en bas de page.

---

## 10. Commandes locales (référence rapide)

### Tout lancer comme en CI (Bash / WSL / Git Bash)

```bash
# 1. Backend
cd RecruitSaas-backend/Recrutement-api.Tests
export APPLY_MIGRATIONS=false
dotnet test -c Release

# 2. Frontend
cd ../../RecruitSaas-frontend
npm ci && npm run lint && VITE_API_ORIGIN=http://localhost:5202 npm run build

# 3. Service IA
cd ../recruit-ai-service
pip install -r requirements.txt -r requirements-dev.txt
GROQ_API_KEY=test-key-for-ci pytest tests/ -v --cov=.

# 4. Intégration
cd ..
bash .github/scripts/ci-integration.sh

# 5. Docker build
docker build -t recruitsaas-backend:local ./RecruitSaas-backend/Recrutement-api
docker build --build-arg VITE_API_ORIGIN=http://localhost:5202 -t recruitsaas-frontend:local ./RecruitSaas-frontend
docker build -t recruitsaas-ai:local ./recruit-ai-service
```

### PowerShell (Windows)

```powershell
# Backend
Set-Location RecruitSaas-backend\Recrutement-api.Tests
$env:APPLY_MIGRATIONS = "false"
dotnet test -c Release

# Frontend
Set-Location ..\..\RecruitSaas-frontend
npm ci; npm run lint
$env:VITE_API_ORIGIN = "http://localhost:5202"; npm run build

# Service IA
Set-Location ..\recruit-ai-service
pip install -r requirements.txt -r requirements-dev.txt
$env:GROQ_API_KEY = "test-key-for-ci"
pytest tests/ -v --cov=.
```

---

## 11. Infrastructure de test backend

### 11.1 Environnement `Testing`

Dans `Program.cs`, le provider EF Core est choisi selon l'environnement :

```csharp
if (builder.Environment.IsEnvironment("Testing"))
    options.UseSqlite(connectionString);   // Tests
else
    options.UseNpgsql(connectionString);   // Production / Docker
```

Cela évite le conflit « double provider » (Npgsql + SQLite simultanés).

### 11.2 `RecruitSaasApiFactory`

| Mécanisme | Rôle |
|-----------|------|
| `UseEnvironment("Testing")` | Active SQLite dans `Program.cs` |
| SQLite `Cache=Shared` | Base en mémoire partagée entre requêtes |
| `_keepAliveConnection` | Connexion statique pour garder la DB vivante |
| `DbInitLock` + `_databaseInitialized` | `EnsureCreated()` appelé une seule fois (évite « table already exists ») |
| `APPLY_MIGRATIONS=false` | Pas de migrations EF en tests |

### 11.3 Collection xUnit `[Collection("Integration")]`

Fichier `IntegrationTestCollection.cs` :

```csharp
[CollectionDefinition("Integration")]
public class IntegrationTestCollection : ICollectionFixture<RecruitSaasApiFactory>;
```

Classes concernées : `HealthEndpointTests`, `AuthApiTests`, `ProtectedEndpointTests`.

**Effets :**
- Une seule instance de `RecruitSaasApiFactory` pour tous les tests d'intégration
- Exécution **séquentielle** au sein de la collection (pas de parallélisme conflictuel)

---

## 12. Dépannage

### Erreur `NU1301` en local (Windows)

```
Impossible de charger l'index de service pour https://api.nuget.org/v3/index.json
```

**Cause :** timeout réseau / proxy / firewall vers NuGet.org.

**Solutions :**
- Vérifier la connexion Internet et le proxy ESPRIT
- Relancer `dotnet restore` plus tard
- **La CI GitHub n'est pas affectée** — les runners ont un accès NuGet fiable

### `table "Notifications" already exists` (SQLite)

**Cause :** plusieurs factories appelaient `EnsureCreated()` en parallèle sur la même base.

**Correctif appliqué :** collection xUnit + verrou statique dans `RecruitSaasApiFactory`.

### `npm ci` échoue en CI

**Cause fréquente :** `package-lock.json` absent ou `.gitignore`.

**Solution :** versionner `RecruitSaas-frontend/package-lock.json`.

### Intégration Docker timeout

**Cause :** build lent du service IA (modèles, dépendances).

**Actions :**
- Vérifier les logs : `docker compose -f docker-compose.ci.yml logs ai-service`
- Le timeout CI est de **60 minutes** pour le job `integration`
- `--wait-timeout 900` (15 min) dans le script bash

### Warnings ESLint en CI

Les warnings (ex. `EntretienView.vue`) **ne bloquent pas** la CI tant qu'ils restent sous `--max-warnings 50`.

---

## 13. Grille de niveau PFE

| Niveau | Critères | Implémenté |
|--------|----------|------------|
| **Correct** | Tests backend unitaires, tests Python simples, build frontend, docker build | ✅ |
| **Très bon** | Tests API backend, lint frontend, tests d'intégration | ✅ |
| **Excellent** | Sanity checks IA, couverture, multi-services, **push GHCR (CD)** | ✅ |

### Récapitulatif quantitatif

| Composant | Tests / vérifications | Outil |
|-----------|----------------------|-------|
| Backend | **21 tests** | xUnit + Coverlet |
| Service IA | **18 tests** | pytest + pytest-cov |
| Frontend | Lint + build | ESLint + Vite |
| Intégration | 4 smoke tests HTTP | Docker Compose + curl |
| Docker | 3 images build + push GHCR | docker/build-push-action |

---

## 14. Extensions possibles (non implémentées)

| Extension | Description |
|-----------|-------------|
| **Vitest** | Tests unitaires composants Vue |
| **Playwright / Cypress** | Tests E2E navigateur |
| **Déploiement VPS** | Pull GHCR + docker compose sur serveur distant |
| **SonarCloud / Codecov** | Analyse qualité + badge couverture |
| **Tests backend supplémentaires** | Candidatures, offres, entretiens avec mocks IA |
| **Matrix CI** | Tests sur plusieurs versions Node / .NET |

---

## Fichiers de référence

| Fichier | Description |
|---------|-------------|
| `.github/workflows/ci.yml` | Workflow CI/CD GitHub Actions |
| `docs/CD.md` | Documentation déploiement continu (GHCR) |
| `.github/scripts/ci-integration.sh` | Script smoke tests Docker |
| `docker-compose.ci.yml` | Stack CI (postgres + backend + IA) |
| `RecruitSaas-backend/Recrutement-api.Tests/` | Projet tests .NET |
| `recruit-ai-service/tests/` | Tests pytest |
| `RecruitSaas-frontend/eslint.config.js` | Configuration ESLint |

---

*Voir aussi : [DOCKER.md](./DOCKER.md) pour le déploiement et le développement local complet.*

*Dernière mise à jour : juin 2026 — pipeline CI validé (5/5 jobs au vert).*
