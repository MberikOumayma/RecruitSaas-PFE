# Conteneurisation Docker — RecruitSaas PFE 2026

Documentation de la mise en place Docker pour la plateforme **TalentFlow / RecruitSaas** : architecture, fichiers créés, modifications du code, commandes et procédure de test/démo.

---

## 1. Objectif

Conteneuriser l'application multi-services afin de :

- Lancer **toute la stack** avec une seule commande (`docker compose up`)
- Garantir un **environnement reproductible** (démo soutenance, développement, future CI)
- Isoler chaque composant (frontend, backend, IA, base de données) dans son propre conteneur
- **Sans hébergement cloud** : exécution locale via Docker Desktop

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     docker compose (applipfe26)                  │
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │   frontend   │     │   backend    │────▶│  ai-service  │   │
│   │  Vue + Nginx │────▶│  ASP.NET 10  │     │   FastAPI    │   │
│   │  :8888 → 80  │     │    :5202     │     │    :8000     │   │
│   └──────────────┘     └──────┬───────┘     └──────────────┘   │
│                               │                                  │
│                               ▼                                  │
│                        ┌──────────────┐                          │
│                        │  postgres    │                          │
│                        │  :5432       │                          │
│                        └──────────────┘                          │
│                                                                  │
│   Réseau interne : recruitsaas-net (bridge)                      │
└─────────────────────────────────────────────────────────────────┘
```

### Services et ports (machine hôte)

| Service        | Conteneur              | Image / build              | Port hôte | Rôle                          |
|----------------|------------------------|----------------------------|-----------|-------------------------------|
| PostgreSQL     | `recruitsaas-db`       | `postgres:16-alpine`       | 5432      | Base de données               |
| Backend API    | `recruitsaas-backend`  | `RecruitSaas-backend/...`  | 5202      | API REST .NET                 |
| Service IA     | `recruitsaas-ai`       | `recruit-ai-service/...`   | 8000      | FastAPI (scoring, NER, etc.)  |
| Frontend       | `recruitsaas-frontend` | `RecruitSaas-frontend/...` | **8888**  | Interface Vue.js (Nginx)      |

> **Note port frontend :** le port **8888** a été choisi car **8080** et **8081** étaient déjà utilisés sur la machine de développement.

---

## 3. Fichiers créés

### 3.1 Racine du projet

| Fichier                 | Description                                      |
|-------------------------|--------------------------------------------------|
| `docker-compose.yml`    | Orchestration des 4 services, réseau, volumes    |
| `.env.docker.example`   | Exemple de variables (mot de passe PostgreSQL)   |

### 3.2 Backend — `RecruitSaas-backend/Recrutement-api/`

| Fichier          | Description                                                |
|------------------|------------------------------------------------------------|
| `Dockerfile`     | Build multi-stage .NET 10 (SDK → runtime aspnet)           |
| `.dockerignore`  | Exclut `bin/`, `obj/`, fichiers secrets locaux             |

### 3.3 Frontend — `RecruitSaas-frontend/`

| Fichier          | Description                                                |
|------------------|------------------------------------------------------------|
| `Dockerfile`     | Build Node 20 + serveur Nginx Alpine                       |
| `nginx.conf`     | Config SPA Vue (fallback `index.html`)                     |
| `.dockerignore`  | Exclut `node_modules/`, `dist/`, `.env`                    |

### 3.4 Service IA — `recruit-ai-service/`

| Fichier          | Description                                                |
|------------------|------------------------------------------------------------|
| `Dockerfile`     | Python 3.12 + Tesseract OCR + dépendances ML               |
| `.dockerignore`  | Exclut `__pycache__/`, `.env`, `chroma_db/`                |
| `models/README.md` | Explique que le modèle NER n'est pas sur GitHub          |

---

## 4. Contenu des Dockerfiles

### 4.1 Backend (.NET 10)

**Stratégie :** build multi-stage pour une image finale légère.

1. **Stage `base`** : image runtime `aspnet:10.0` + bibliothèque `libgssapi-krb5-2` (connexion PostgreSQL/Npgsql)
2. **Stage `build`** : image `sdk:10.0`, `dotnet restore` + `dotnet publish`
3. **Stage `final`** : copie du publish, entrypoint `dotnet Recrutement-api.dll`

Port exposé : **5202**

### 4.2 Frontend (Vue 3 + Vite + Nginx)

1. **Stage `build`** : `npm ci` puis `npm run build` avec variable `VITE_API_ORIGIN`
2. **Stage final** : Nginx sert le dossier `dist/`

Le build injecte l'URL du backend :

```dockerfile
ARG VITE_API_ORIGIN=http://localhost:5202
ENV VITE_API_ORIGIN=$VITE_API_ORIGIN
```

Nginx écoute sur le port **80** dans le conteneur ; mappé sur **8888** côté hôte.

### 4.3 Service IA (Python / FastAPI)

- Base : `python:3.12-slim`
- Paquets système : **Tesseract OCR** (extraction texte CV), OpenGL libs (OpenCV)
- Installation : `pip install -r requirements.txt` (torch, spacy, fastapi, etc.)
- Démarrage : `uvicorn main:app --host 0.0.0.0 --port 8000`

**Durée du premier build :** 30 à 60 minutes (téléchargement PyTorch et dépendances NVIDIA).

---

## 5. Fichier `docker-compose.yml` — points clés

### PostgreSQL

- Volume persistant `postgres_data` pour conserver les données entre redémarrages
- **Healthcheck** : le backend attend que PostgreSQL soit prêt (`service_healthy`)

### Service IA

- Fichier secrets : `recruit-ai-service/.env` (clé `GROQ_API_KEY`)
- **Volume monté** pour le modèle NER (~500 Mo, non versionné sur GitHub) :

```yaml
volumes:
  - ./recruit-ai-service/models/cv_ner_roberta_best:/app/models/cv_ner_roberta_best:ro
```

### Backend

Variables d'environnement importantes :

| Variable | Valeur Docker | Rôle |
|----------|---------------|------|
| `ConnectionStrings__DefaultConnection` | `Host=postgres;...` | Connexion DB via nom du service Docker |
| `AiService__BaseUrl` | `http://ai-service:8000` | Appels HTTP vers le conteneur IA |
| `Frontend__Url` | `http://localhost:8888` | CORS |
| `APPLY_MIGRATIONS` | `true` | Applique les migrations EF Core au démarrage |
| `ASPNETCORE_URLS` | `http://+:5202` | Port d'écoute |

### Frontend

- Dépend du backend (`depends_on`)
- Build arg : `VITE_API_ORIGIN: http://localhost:5202`

### Réseau

Tous les services partagent le réseau **`recruitsaas-net`** (driver bridge).  
Les conteneurs se joignent par **nom de service** (`postgres`, `ai-service`, `backend`).

---

## 6. Modifications du code applicatif

Pour que Docker fonctionne, les fichiers suivants ont été adaptés :

### 6.1 `Program.cs` (backend)

- **CORS** : ajout de `http://localhost:8888` (et origines configurables via `Frontend:Url`)
- **Migrations automatiques** si `APPLY_MIGRATIONS=true` :

```csharp
if (string.Equals(builder.Configuration["APPLY_MIGRATIONS"], "true", ...))
{
    scope.ServiceProvider.GetRequiredService<ApplicationDbContext>().Database.Migrate();
}
```

- **Fichiers statiques** (images CV) : CORS pour le port 8888

### 6.2 `AiOrchestratorService.cs`

- URL du service IA lue depuis la configuration au lieu d'une adresse en dur :

```csharp
var baseUrl = configuration["AiService:BaseUrl"]?.TrimEnd('/') ?? "http://127.0.0.1:8000";
_aiBaseUrl = $"{baseUrl}/ai";
```

### 6.3 `appsettings.json`

- Section ajoutée :

```json
"AiService": {
  "BaseUrl": "http://127.0.0.1:8000"
}
```

(Surchargée en Docker par `AiService__BaseUrl`.)

### 6.4 `api.js` (frontend)

- Utilisation de la variable Vite au build :

```javascript
const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || "http://localhost:5202"
const api = axios.create({ baseURL: `${API_ORIGIN}/api` })
```

### 6.5 Migrations Entity Framework (base Docker vierge)

Problème rencontré : la migration `InitialCreate` était **commentée**, et des migrations antérieures tentaient de modifier des tables inexistantes.

**Corrections :**

- Décommenter le corps de `20260409162009_InitialCreate.cs`
- Ajouter les colonnes `Telephone` et `Phone` directement dans `InitialCreate`
- Neutraliser (no-op) les migrations `AddTelephoneToUtilisateur` et `AddPhoneToExpert` qui s'exécutaient avant la création des tables

---

## 7. Prérequis

1. **Docker Desktop** installé et démarré (Engine running)
2. **Fichier** `recruit-ai-service/.env` :

```env
GROQ_API_KEY=votre_cle_groq
```

3. **Dossier local** (non sur GitHub) :

```
recruit-ai-service/models/cv_ner_roberta_best/
```

4. Connexion Internet stable pour le **premier** `docker compose up --build`

---

## 8. Commandes essentielles

### 8.1 Premier lancement (build + démarrage)

```powershell
cd "C:\Users\Oumaima\OneDrive - ESPRIT\Bureau\appliPFE26"
docker compose up --build
```

### 8.2 Lancement en arrière-plan

```powershell
docker compose up -d
```

### 8.3 Vérifier l'état des conteneurs

```powershell
docker compose ps
```

Résultat attendu : **4 conteneurs** `Up`.

### 8.4 Consulter les logs

```powershell
docker compose logs backend
docker compose logs ai-service
docker compose logs frontend
docker compose logs postgres
```

Logs en temps réel :

```powershell
docker compose logs -f backend
```

### 8.5 Arrêter les conteneurs

```powershell
docker compose down
```

### 8.6 Arrêter et supprimer la base de données

```powershell
docker compose down -v
```

À utiliser après une erreur de migration ou pour repartir d'une base vide.

### 8.7 Reconstruire un seul service

```powershell
docker compose up -d --build backend
docker compose up -d --build frontend
```

---

## 9. Tests de validation

### 9.1 Checklist

| # | Test | URL / commande | Résultat attendu |
|---|------|----------------|------------------|
| 1 | Conteneurs actifs | `docker compose ps` | 4 services `Up` |
| 2 | Frontend | http://localhost:8888 | Page TalentFlow |
| 3 | Backend health | http://localhost:5202/health | `{"status":"Healthy",...}` |
| 4 | API IA | http://localhost:8000/docs | Swagger RecruitSaaS AI Service |
| 5 | Parcours métier | Login sur :8888 | Navigation application |

### 9.2 Captures recommandées (soutenance / rapport)

1. Terminal : sortie de `docker compose ps`
2. Docker Desktop : 4 conteneurs running
3. Navigateur : localhost:8888, :5202/health, :8000/docs
4. Extraits de `docker-compose.yml` et d'un `Dockerfile`

---

## 10. Problèmes rencontrés et solutions

| Problème | Cause | Solution appliquée |
|----------|-------|-------------------|
| Push GitHub refusé (>100 Mo) | Modèle NER `transformer/model` ~479 Mo | Exclu du repo (`.gitignore`), monté en volume Docker |
| Push GitHub (secrets) | Clés OAuth / SMTP dans `appsettings` | Remplacement par placeholders dans le repo |
| Backend crash au démarrage | Migrations EF dans le mauvais ordre + `InitialCreate` commenté | Correction des migrations (voir §6.5) |
| `libgssapi_krb5.so.2` manquant | Image .NET minimale | `apt-get install libgssapi-krb5-2` dans Dockerfile backend |
| Port 8080 / 8081 indisponible | Autre application sur la machine | Frontend mappé sur **8888:80** |
| Frontend absent dans Docker Desktop | Port bloqué → conteneur `Created` mais pas `Up` | Changer le port + `docker compose up -d frontend` |
| Seulement 2 conteneurs visibles dans l'UI | Liste tronquée / groupe non déplié | Utiliser `docker compose ps` ou déplier `applipfe26` |

---

## 11. Démo soutenance (script 5–7 min)

1. **Contexte** : « Application multi-services conteneurisée avec Docker Compose. »
2. **Fichiers** : montrer `docker-compose.yml` + un `Dockerfile`.
3. **Terminal** : `docker compose ps` → 4 conteneurs.
4. **Docker Desktop** : conteneurs verts, ports 8888 / 5202 / 8000 / 5432.
5. **Navigateur** :
   - http://localhost:8888 — application
   - http://localhost:5202/health — santé API
   - http://localhost:8000/docs — documentation IA
6. **Fonctionnel** : connexion + une fonctionnalité (liste candidats, offre, etc.).
7. **Limites** : déploiement local, modèle NER en volume, pas de serveur cloud (CI/CD à venir).

**Phrase de conclusion :**

> « Docker garantit que toute l'équipe — ou le jury — peut lancer la plateforme complète avec une commande, sans installer manuellement .NET, Node, Python et PostgreSQL sur la machine hôte. »

---

## 12. Structure des fichiers Docker (arborescence)

```
appliPFE26/
├── docker-compose.yml
├── .env.docker.example
├── RecruitSaas-backend/Recrutement-api/
│   ├── Dockerfile
│   └── .dockerignore
├── RecruitSaas-frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .dockerignore
└── recruit-ai-service/
    ├── Dockerfile
    ├── .dockerignore
    ├── .env                    (local, non versionné)
    └── models/
        ├── README.md
        └── cv_ner_roberta_best/  (local, volume Docker)
```

---

## 13. Prochaines étapes (hors scope Docker local)

- **CI GitHub Actions** : build automatique backend / frontend / IA à chaque push
- **CD partiel** : `docker build` dans la pipeline + push vers GitHub Container Registry (GHCR)
- **Optimisation image IA** : variante PyTorch CPU-only pour réduire taille et temps de build

---

## 14. Références

- Documentation Docker Compose : https://docs.docker.com/compose/
- Images .NET officielles : https://hub.docker.com/_/microsoft-dotnet
- Repository GitHub du projet : https://github.com/MberikOumayma/RecruitSaas-PFE

---

*Document rédigé dans le cadre du PFE 2026 — RecruitSaas / TalentFlow.*
