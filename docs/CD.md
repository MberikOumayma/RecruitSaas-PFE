# Déploiement continu (CD) — GitHub Container Registry

Guide du **CD sans hébergement** : la pipeline build, valide et **publie automatiquement** les images Docker sur [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) (GHCR).

> **Pas de VPS requis.** Les images sont stockées gratuitement sur GitHub. Aucun serveur de production n'est nécessaire pour démontrer le CD dans un rapport PFE.

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [CI vs CD dans ce projet](#2-ci-vs-cd-dans-ce-projet)
3. [Architecture du pipeline complet](#3-architecture-du-pipeline-complet)
4. [Images publiées sur GHCR](#4-images-publiées-sur-ghcr)
5. [Configuration workflow](#5-configuration-workflow)
6. [Quand les images sont poussées](#6-quand-les-images-sont-poussées)
7. [Consulter les packages sur GitHub](#7-consulter-les-packages-sur-github)
8. [Tirer une image en local](#8-tirer-une-image-en-local)
9. [Phrase pour le rapport PFE](#9-phrase-pour-le-rapport-pfe)
10. [Dépannage](#10-dépannage)

---

## 1. Vue d'ensemble

| Élément | Détail |
|---------|--------|
| **Registry** | `ghcr.io` (GitHub Container Registry) |
| **Coût** | Gratuit pour les repos publics ; quota généreux pour les privés |
| **Authentification CI** | `GITHUB_TOKEN` (automatique, aucun secret à créer) |
| **Services packagés** | Backend .NET, Frontend Vue, Service IA Python |
| **Fichier workflow** | `.github/workflows/ci.yml` (nom affiché : **CI/CD**) |

---

## 2. CI vs CD dans ce projet

| Phase | Objectif | Déclencheur |
|-------|----------|-------------|
| **CI** | Tests, lint, build, intégration Docker Compose | Push **et** Pull Request sur `main` |
| **CD** | Build + push des images vers GHCR | Push sur `main` **uniquement** |

Sur une **Pull Request**, les images Docker sont **construites** (validation du Dockerfile) mais **non poussées** sur GHCR.

---

## 3. Architecture du pipeline complet

```
Push / PR sur main
        │
        ├── build-backend   ──┐
        ├── build-frontend  ──┼──▶ integration ──▶ docker-build
        └── build-ai        ──┘                      │
                                                     ├── Build × 3 (toujours)
                                                     └── Push GHCR (main seulement)
                                                              │
                                                              ▼
                                              ghcr.io/<owner>/recruitsaas-*
                                              tags: latest + <commit-sha>
```

**Durée totale typique :** ~10 minutes (build + push inclus).

---

## 4. Images publiées sur GHCR

Remplace `<owner>` par le nom d'utilisateur ou l'organisation GitHub (en minuscules).

| Service | Nom du package | Tags |
|---------|----------------|------|
| Backend API | `ghcr.io/<owner>/recruitsaas-backend` | `latest`, `<sha-commit>` |
| Frontend Vue | `ghcr.io/<owner>/recruitsaas-frontend` | `latest`, `<sha-commit>` |
| Service IA | `ghcr.io/<owner>/recruitsaas-ai` | `latest`, `<sha-commit>` |

**Exemple concret** (repo `MberikOumayma/RecruitSaas-PFE`) :

```
ghcr.io/mberikoumayma/recruitsaas-backend:latest
ghcr.io/mberikoumayma/recruitsaas-frontend:latest
ghcr.io/mberikoumayma/recruitsaas-ai:latest
```

Le tag `<sha-commit>` permet de retrouver l'image exacte d'un run CI donné (reproductibilité).

---

## 5. Configuration workflow

Extrait du job `docker-build` dans `.github/workflows/ci.yml` :

```yaml
permissions:
  contents: read
  packages: write

env:
  REGISTRY: ghcr.io

# ...

- name: Log in to GitHub Container Registry
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build & push backend image
  uses: docker/build-push-action@v6
  with:
    context: ./RecruitSaas-backend/Recrutement-api
    push: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    tags: |
      ghcr.io/<owner>/recruitsaas-backend:latest
      ghcr.io/<owner>/recruitsaas-backend:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Points clés :**

- **`packages: write`** — autorise le push vers GHCR via `GITHUB_TOKEN`
- **Namespace en minuscules** — GHCR exige des noms d'images en lowercase
- **Cache GHA** — accélère les builds suivants (layers Docker réutilisés)
- **Résumé du job** — tableau des URLs d'images dans l'onglet Summary du workflow

---

## 6. Quand les images sont poussées

| Événement | Branche | Build Docker | Push GHCR |
|-----------|---------|--------------|-----------|
| Push | `main` | ✅ | ✅ |
| Pull Request | `main` | ✅ | ❌ |
| Push | autre branche | ❌ (workflow non déclenché) | ❌ |

---

## 7. Consulter les packages sur GitHub

1. Ouvrir le repo sur GitHub
2. Barre latérale droite → **Packages** (ou profil → **Your packages**)
3. Trois packages visibles :
   - `recruitsaas-backend`
   - `recruitsaas-frontend`
   - `recruitsaas-ai`

Chaque package affiche les tags (`latest`, SHA du commit), la date de publication et la taille de l'image.

**Capture recommandée pour le rapport :** page Packages + résumé du job « Docker Build & Push (GHCR) » avec le tableau d'images.

---

## 8. Tirer une image en local

Les packages liés au repo sont en général accessibles aux collaborateurs du projet. Pour un repo **public**, les images peuvent être publiques après configuration du package.

**Connexion (une fois) :**

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u VOTRE_USER --password-stdin
```

> Créer un Personal Access Token (PAT) avec scope `read:packages` sur GitHub → Settings → Developer settings.

**Télécharger une image :**

```bash
docker pull ghcr.io/<owner>/recruitsaas-backend:latest
docker pull ghcr.io/<owner>/recruitsaas-frontend:latest
docker pull ghcr.io/<owner>/recruitsaas-ai:latest
```

**Lancer le backend seul (exemple) :**

```bash
docker run --rm -p 5202:5202 \
  -e ConnectionStrings__DefaultConnection="Host=host.docker.internal;..." \
  ghcr.io/<owner>/recruitsaas-backend:latest
```

Pour une stack complète, préférer `docker-compose` local — voir [DOCKER.md](./DOCKER.md).

---

## 9. Phrase pour le rapport PFE

> *« La pipeline CI/CD automatisée exécute l'ensemble des tests (unitaires, API, intégration multi-services), construit les trois images Docker de l'application (backend ASP.NET Core, frontend Vue.js, microservice IA Python), puis les publie sur GitHub Container Registry à chaque merge sur la branche `main`. Aucun déploiement sur serveur distant n'est requis : le CD garantit que des artefacts containerisés versionnés et reproductibles sont produits automatiquement et disponibles pour un déploiement futur. »*

**Points à mettre en avant à l'oral :**

- Séparation CI (validation) / CD (publication d'artefacts)
- Registry gratuit intégré à GitHub (pas de Docker Hub payant)
- Tag `latest` + tag SHA pour la traçabilité
- Pas de push sur les PR (évite de polluer le registry)

---

## 10. Dépannage

### Package privé / 403 au pull

Par défaut, les packages GHCR peuvent être **privés**. Sur la page du package → **Package settings** → **Change visibility** ou lier le package au repo public.

### Push échoue avec « permission denied »

Vérifier que le workflow contient :

```yaml
permissions:
  packages: write
```

### Nom d'image invalide

GHCR n'accepte que des noms en **minuscules**. Le workflow applique `${GITHUB_REPOSITORY_OWNER,,}` automatiquement.

### Build lent

Le cache GitHub Actions (`cache-from` / `cache-to: type=gha`) réduit la durée des builds suivants.

---

## Fichiers liés

| Fichier | Rôle |
|---------|------|
| `.github/workflows/ci.yml` | Pipeline CI/CD complète |
| `RecruitSaas-backend/Recrutement-api/Dockerfile` | Image backend |
| `RecruitSaas-frontend/Dockerfile` | Image frontend |
| `recruit-ai-service/Dockerfile` | Image service IA |
| [CI.md](./CI.md) | Documentation tests et CI |
| [DOCKER.md](./DOCKER.md) | Docker Compose local |

---

*Dernière mise à jour : juin 2026*
