# Intégration continue (CI) — GitHub Actions

Pipeline CI pour **RecruitSaas / TalentFlow** : vérifie automatiquement que le code compile et que les images Docker se construisent à chaque push sur `main`.

---

## 1. Fichier de workflow

**Emplacement :** `.github/workflows/ci.yml`

**Déclencheurs :**
- Push sur la branche `main`
- Pull Request vers `main`

---

## 2. Jobs exécutés

| Job | Action | Durée estimée |
|-----|--------|---------------|
| `build-backend` | `dotnet build` + **xUnit** (`/health`) | ~3 min |
| `build-frontend` | `npm ci` + `npm run build` | ~3 min |
| `build-ai` | `pip install` + **pytest** (`GET /`) | ~10–20 min |
| `docker-build` | `docker build` × 3 (backend, frontend, IA) | ~30–60 min |

Le job **docker-build** ne démarre que si les 3 builds précédents réussissent.

---

## 3. Détail des jobs

### 3.1 Backend (.NET 10)

**Projet de tests :** `RecruitSaas-backend/Recrutement-api.Tests/` (xUnit + `WebApplicationFactory`)

```yaml
dotnet build   # Recrutement-api
dotnet test    # Recrutement-api.Tests — vérifie GET /health → Healthy
```

Test inclus : `HealthEndpointTests.GetHealth_ReturnsHealthyStatus`

### 3.2 Frontend (Vue 3 + Vite)

`package-lock.json` doit être versionné (requis par `npm ci` en CI).

```yaml
working-directory: RecruitSaas-frontend
npm ci
npm run build   # avec VITE_API_ORIGIN=http://localhost:5202
```

### 3.3 Service IA (Python 3.12)

**Tests :** `recruit-ai-service/tests/test_health.py` (pytest + FastAPI TestClient)

```yaml
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v    # vérifie GET / → status ok
```

Variable CI : `GROQ_API_KEY=test-key-for-ci` (requis au démarrage de `main.py`).

### 3.4 Docker Build

Construit les 3 images **sans les pousser** (vérification des Dockerfiles uniquement) :

```bash
docker build -t recruitsaas-backend:ci ./RecruitSaas-backend/Recrutement-api
docker build --build-arg VITE_API_ORIGIN=http://localhost:5202 -t recruitsaas-frontend:ci ./RecruitSaas-frontend
docker build -t recruitsaas-ai:ci ./recruit-ai-service
```

Timeout du job : **120 minutes** (PyTorch + dépendances IA).

---

## 4. Mettre en place sur GitHub

### 4.1 Committer et pousser le workflow

```powershell
cd "C:\Users\Oumaima\OneDrive - ESPRIT\Bureau\appliPFE26"
git add .github/workflows/ci.yml docs/CI.md
git commit -m "Add GitHub Actions CI pipeline"
git push origin main
```

### 4.2 Voir les résultats

1. Ouvrir https://github.com/MberikOumayma/RecruitSaas-PFE
2. Onglet **Actions**
3. Cliquer sur le workflow **CI** en cours ou terminé
4. Vérifier que les 4 jobs sont **verts** ✓

---

## 5. Schéma du pipeline

```
Push / PR sur main
        │
        ├── build-backend   ──┐
        ├── build-frontend  ──┼──▶ docker-build
        └── build-ai        ──┘
                                    (si les 3 OK)
```

---

## 6. Démo soutenance

**Phrase :**

> « À chaque push sur GitHub, la pipeline CI compile le backend .NET, le frontend Vue, installe les dépendances Python du service IA, puis vérifie que les trois Dockerfiles se construisent correctement. »

**À montrer :**
1. Fichier `.github/workflows/ci.yml` dans le repo
2. Onglet **Actions** GitHub avec runs réussis (captures d'écran)
3. Détail d'un job (logs `dotnet build`, `npm run build`, etc.)

---

## 7. Tests automatisés

| Composant | Framework | Fichiers | Couverture actuelle |
|-----------|-----------|----------|---------------------|
| Backend | xUnit | `Recrutement-api.Tests/HealthEndpointTests.cs` | Endpoint `/health` |
| Service IA | pytest | `recruit-ai-service/tests/test_health.py` | Endpoint `/` |
| Frontend | — | *(aucun)* | Pas de Vitest/Jest configuré |

> Le frontend est validé par **`npm run build`** (compilation). Des tests unitaires Vue pourront être ajoutés plus tard avec Vitest.

### Lancer les tests en local

```powershell
# Backend
cd RecruitSaas-backend/Recrutement-api.Tests
dotnet test

# Service IA
cd recruit-ai-service
pip install -r requirements.txt -r requirements-dev.txt
$env:GROQ_API_KEY="test-key"
pytest tests/ -v
```

---

## 8. Limites actuelles

| Élément | Statut |
|---------|--------|
| Build automatique | ✅ Oui |
| Tests backend + IA | ✅ Oui (health checks) |
| Tests frontend unitaires | ❌ Non |
| Push images Docker (GHCR) | ❌ Non (étape CD suivante) |
| Déploiement cloud | ❌ Non (hébergement local) |

---

## 9. Prochaine étape (CD partiel)

- Push des images vers **GitHub Container Registry (GHCR)**
- Déclenchement sur tag ou push `main`
- Toujours sans serveur de production (images prêtes à déployer)

---

*Voir aussi : [DOCKER.md](./DOCKER.md)*
