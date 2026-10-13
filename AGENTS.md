# CleanHome — Contexte projet pour agents IA

> Ce fichier sert de **source de vérité** pour tout agent IA (Claude, Cursor, Copilot,
> GPT, etc.) qui intervient sur ce projet. **Lis-le entièrement avant toute
> modification de code.** Si une demande utilisateur contredit ce fichier,
> demande confirmation avant d'agir.

---

## 1. Nature du projet

**CleanHome** est une plateforme web de réservation de **services de ménage à domicile**
(Côte d'Ivoire, prix en FCFA). Elle permet à un particulier de :
1. parcourir un catalogue de prestations de ménage ;
2. consulter le détail d'une prestation ;
3. réserver une prestation (date + adresse) ;
4. consulter ses réservations.

Un administrateur peut :
1. se connecter à un espace dédié ;
2. ajouter / modifier / supprimer des prestations ;
3. consulter les réservations et changer leur statut.

**Référence fonctionnelle complète** : voir `BRIEF_UIUX.md` (fourni séparément).
C'est un document contractuel — **aucune fonctionnalité hors brief ne doit être ajoutée
sans validation explicite.**

### Périmètre INTERDIT (ne jamais implémenter sans demande explicite)

- ❌ Paiement en ligne (Wave, Orange Money, CB, PayPal, Stripe…)
- ❌ Système de notation / avis / commentaires
- ❌ Favoris, coupons, abonnements, portefeuille
- ❌ Chat, messagerie, notifications push
- ❌ Géolocalisation, carte, GPS
- ❌ Gestion des employés / RH
- ❌ Statistiques avancées, graphiques, dashboards analytiques
- ❌ Marketplace multi-métiers (plomberie, électricité, jardinage…) — **ménage uniquement**
- ❌ Page "À propos", "Équipe", "Blog", "FAQ", landing marketing multi-sections
- ❌ Connexion sociale (Google / Facebook / Apple)

---

## 2. Stack technique

### Backend
- **Python 3.11+** (⚠️ éviter Python 3.14 — incompatibilités pydantic-core)
- **FastAPI** (framework web)
- **Uvicorn** (serveur ASGI)
- **SQLAlchemy 2.x** (ORM, style `DeclarativeBase`)
- **Pydantic v2** (validation)
- **SQLite** en dev (migration PostgreSQL prévue plus tard)
- **JWT** (via `python-jose`) pour l'authentification
- **passlib[bcrypt]** pour le hachage des mots de passe
- **Jinja2** pour le rendu HTML côté serveur (⚠️ pas de SPA, pas de React/Vue)

### Front
- **HTML + CSS + JS vanilla**
- **Jinja2** pour les templates (héritage via `base.html`)
- **CSS centralisé** dans `static/css/cleanhome.css`
- **JS centralisé** dans `static/js/cleanhome.js`
- **Pas de framework front** (pas de React, Vue, Alpine, HTMX, Tailwind, Bootstrap)
- Police : **DM Sans** (corps) + **Plus Jakarta Sans** (titres), via Google Fonts
- Palette : vert émeraude (`--green-700: #087d6b`) + blancs cassés

### Ce qui N'EST PAS utilisé
- ❌ Django, Flask, Laravel
- ❌ Alembic pour l'instant (à introduire au Palier 7)
- ❌ Docker (pas encore)
- ❌ Tests automatisés (prévus au Palier 7)
- ❌ Dépendances externes non listées dans `requirements.txt`

---

## 3. Architecture backend

Architecture **en couches** (inspirée du MVC, adaptée FastAPI) :

**Règles strictes :**

1. **`web/`** contient les routes HTML (renvoient `TemplateResponse`)
2. **`api/`** contient les routes JSON (renvoient dict / Pydantic)
3. **`services/`** contient **toute la logique métier** — jamais de SQL ici
4. **`repositories/`** contient **tout l'accès BDD** — jamais de logique métier ici
5. **`models/`** contient les tables SQLAlchemy **uniquement**
6. **`schemas/`** contient les schémas Pydantic (validation entrée/sortie)
7. **`core/`** contient les briques transverses (security, dependencies)
8. **Une route ne doit JAMAIS** :
   - écrire une requête SQL directement
   - contenir une règle métier (ex: "vérifier que l'utilisateur existe déjà")
   - faire plus de 15 lignes (hors décorateur)

### Arborescence cible
cleanhome/
├── app/
│ ├── main.py # create_app(), monte tout
│ ├── config.py # Settings (Pydantic BaseSettings)
│ ├── database.py # engine, SessionLocal, Base
│ ├── core/
│ │ ├── security.py # hash_password, JWT encode/decode
│ │ └── dependencies.py # get_db, get_current_user, require_admin
│ ├── models/ # tables SQLAlchemy
│ │ ├── user.py
│ │ ├── service.py
│ │ └── booking.py
│ ├── schemas/ # Pydantic (validation)
│ │ ├── user.py
│ │ ├── service.py
│ │ ├── booking.py
│ │ └── token.py
│ ├── repositories/ # accès BDD
│ │ ├── user_repository.py
│ │ ├── service_repository.py
│ │ └── booking_repository.py
│ ├── services/ # logique métier
│ │ ├── auth_service.py
│ │ ├── service_service.py
│ │ └── booking_service.py
│ ├── web/ # routes HTML (Jinja2)
│ │ ├── auth_pages.py
│ │ ├── public_pages.py
│ │ ├── client_pages.py
│ │ └── admin_pages.py
│ └── api/ # routes JSON (mobile futur)
│ └── v1/
│ ├── router.py
│ └── routes/
│ ├── auth.py
│ ├── services.py
│ ├── bookings.py
│ └── admin.py
├── templates/ # Jinja2
│ ├── base.html
│ ├── partials/
│ │ ├── header.html
│ │ ├── service_card.html
│ │ └── status_badge.html
│ ├── public/
│ │ ├── index.html
│ │ └── service_detail.html
│ ├── auth/
│ │ ├── login.html
│ │ └── register.html
│ ├── client/
│ │ ├── book.html
│ │ ├── confirmation.html
│ │ └── reservations.html
│ └── admin/
│ ├── services.html
│ ├── service_new.html
│ ├── service_edit.html
│ └── reservations.html
├── static/
│ ├── css/cleanhome.css
│ ├── js/cleanhome.js
│ └── img/
├── tests/
├── .env # jamais commit
├── .env.example
├── .gitignore
├── requirements.txt
├── AGENTS.md # ce fichier
└── README.md


---

## 4. Modèle de données

### `User`
| Champ | Type | Contraintes |
|---|---|---|
| `id` | int | PK |
| `full_name` | str(120) | obligatoire |
| `email` | str(180) | unique, indexé, obligatoire |
| `phone` | str(30) | obligatoire |
| `hashed_password` | str(255) | obligatoire |
| `is_admin` | bool | défaut `False` |
| `created_at` | datetime | auto |

### `Service` (prestation de ménage)
| Champ | Type | Contraintes |
|---|---|---|
| `id` | int | PK |
| `name` | str(120) | obligatoire |
| `category` | str(80) | obligatoire, indexé, **saisie libre** (pas d'enum) |
| `description` | text | obligatoire |
| `price` | int | en FCFA, > 0 |
| `duration` | str(50) | ex: "3 heures" |
| `image_url` | str(500) | nullable |
| `created_at` | datetime | auto |

### `Booking` (réservation)
| Champ | Type | Contraintes |
|---|---|---|
| `id` | int | PK |
| `user_id` | int | FK → users.id |
| `service_id` | int | FK → services.id |
| `date` | date | obligatoire |
| `address` | str(255) | obligatoire |
| `phone` | str(30) | obligatoire |
| `price` | int | **snapshot** du prix au moment de la réservation |
| `status` | str(20) | `pending` \| `confirmed` \| `done` \| `cancelled` — défaut `pending` |
| `created_at` | datetime | auto |

**Statuts autorisés** (jamais d'autres valeurs) :
- `pending` → "En attente"
- `confirmed` → "Confirmée"
- `done` → "Terminée"
- `cancelled` → "Annulée"

---

## 5. Routes prévues (contrat)

### Routes HTML (`web/`)

| Méthode | URL | Rôle | Auth |
|---|---|---|---|
| GET | `/` | Catalogue | Public |
| GET | `/service/{id}` | Détail prestation | Public |
| GET | `/login` | Formulaire connexion | Public |
| POST | `/login` | Traitement connexion | Public |
| GET | `/register` | Formulaire inscription | Public |
| POST | `/register` | Traitement inscription | Public |
| GET | `/logout` | Déconnexion (efface cookie) | Public |
| GET | `/book/{service_id}` | Formulaire réservation | Client |
| POST | `/book/{service_id}` | Traitement réservation | Client |
| GET | `/confirmation/{booking_id}` | Page succès | Client |
| GET | `/reservations` | Mes réservations | Client |
| GET | `/admin/services` | Liste prestations | Admin |
| GET | `/admin/services/new` | Formulaire ajout | Admin |
| POST | `/admin/services/new` | Traitement ajout | Admin |
| GET | `/admin/services/{id}/edit` | Formulaire modification | Admin |
| POST | `/admin/services/{id}/edit` | Traitement modification | Admin |
| POST | `/admin/services/{id}/delete` | Suppression | Admin |
| GET | `/admin/reservations` | Liste réservations | Admin |
| POST | `/admin/bookings/{id}/status` | Changement statut | Admin |

### Routes JSON (`api/v1/`) — à venir, prévues pour mobile

Mêmes ressources, préfixées `/api/v1`, réponses JSON.

**Convention de nommage des tags FastAPI :**
- `pages:public`, `pages:auth`, `pages:client`, `pages:admin`
- `api:auth`, `api:services`, `api:bookings`, `api:admin`

---

## 6. Authentification (choix arrêtés)

- **JWT** signé HS256, payload `{"sub": "<user_id>", "is_admin": <bool>, "exp": <timestamp>}`
- **Stockage** : cookie `httponly`, `samesite="lax"`, jamais en localStorage
- **Nom du cookie** : `access_token`
- **Durée** : 24h (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Hachage** : bcrypt via `passlib`
- **Pas de refresh token** (complexité non justifiée à ce stade)
- **Pas de OAuth, pas de connexion sociale**

Dépendances FastAPI attendues dans `core/dependencies.py` :
- `get_db()` : yield une session SQLAlchemy
- `get_current_user(request, db)` : renvoie `User | None` (ne lève pas d'erreur)
- `require_user(user)` : lève 401 si non connecté
- `require_admin(user)` : lève 403 si non admin

---

## 7. Conventions de code

### Python
- **Type hints systématiques** (params, retours)
- **Imports absolus** : `from app.models.user import User`
- **Docstrings courtes** pour les services et repositories
- **Pas de `print()`** — utiliser `logging` si nécessaire
- **Pas de code commenté** laissé en place
- **Lignes < 100 caractères**

### Nommage
- Fichiers Python : `snake_case.py`
- Classes : `PascalCase`
- Fonctions/variables : `snake_case`
- Constantes : `UPPER_SNAKE_CASE`
- Templates : `snake_case.html` sauf `base.html` et `partials/`

### Routes
- Toujours un `APIRouter` par module (jamais de route dans `main.py`)
- Toujours `prefix=` et `tags=` explicites
- Retour HTML : `response_class=HTMLResponse` + `TemplateResponse`
- Retour JSON : `response_model=` quand applicable

### Templates Jinja2
- Toujours `{% extends "base.html" %}` sauf `base.html` et `partials/`
- Toujours définir `{% block title %}`
- Utiliser `url_for('static', path='...')` pour les assets
- Utiliser `{% include "partials/..." %}` pour les fragments
- Ne jamais mettre de logique métier dans un template

### Réponses aux erreurs

- HTML : renvoyer le template avec `error` dans le contexte
- JSON : `raise HTTPException(status_code=..., detail="...")`
- Ne jamais exposer une stack trace en production

---

## 8. Variables d'environnement (`.env`)

DATABASE_URL=sqlite:///./cleanhome.db
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=CleanHome
APP_ENV=development


Accès **uniquement** via `app.config.settings` (jamais `os.getenv` directement).

---

## 9. Règles pour l'agent IA

### ✅ À faire systématiquement

1. **Lire ce fichier** avant toute intervention
2. **Respecter l'architecture en couches** : router → service → repository → model
3. **Créer un service** dès qu'une route contient de la logique métier
4. **Créer un repository** dès qu'une route touche la BDD
5. **Utiliser Pydantic** pour valider les entrées JSON
6. **Utiliser `Form(...)`** pour les entrées de formulaires HTML
7. **Utiliser `TemplateResponse`** pour toute page HTML
8. **Toujours typer** les signatures de fonctions
9. **Toujours proposer les tests** pour une nouvelle route (même minimaux)
10. **Signaler les impacts** sur les autres couches avant de modifier

### ❌ À ne jamais faire

1. ❌ Ajouter une fonctionnalité **hors du brief UI/UX**
2. ❌ Mettre du SQL dans une route ou un service
3. ❌ Mettre de la logique métier dans une route ou un repository
4. ❌ Retourner du HTML en concaténant des strings Python
5. ❌ Utiliser un autre moteur de template que Jinja2
6. ❌ Ajouter un framework front (React, Vue, Alpine, HTMX, Tailwind…)
7. ❌ Modifier la structure des tables sans migration Alembic
8. ❌ Stocker un JWT en localStorage (côté front)
9. ❌ Exposer `hashed_password` dans une réponse API
10. ❌ Réinventer une fonctionnalité déjà présente (`hash_password`, `get_db`, etc.)

### 🤔 En cas d'ambiguïté

- **Demander confirmation** avant d'ajouter une fonctionnalité non listée
- **Proposer une alternative** plutôt que d'inventer
- **Signaler** si une demande viole une règle de la section 4
- **Ne pas "améliorer"** sans demande (pas de refactor spontané)

---

## 10. État d'avancement (à mettre à jour régulièrement)

- [x] Front HTML maquetté (10 pages) — voir `templates/`
- [x] CSS + JS centralisés — voir `static/`
- [x] Brief UI/UX validé — voir `BRIEF_UIUX.md`
- [x] Arborescence backend définie — voir section 3
- [x] Fichiers de base créés (`main.py`, `config.py`, `database.py`, `models/`, `schemas/`, `core/`)
- [x] **Palier 1** — Paramètres et validation
- [x] **Palier 2** — Jinja2 et formulaires
- [x] **Palier 3** — `APIRouter` et structuration
- [x] **Palier 4** — SQLAlchemy et BDD
- [x] **Palier 5** — Authentification JWT
- [x] **Palier 6** — Assemblage CleanHome complet
- [ ] **Palier 7** — Alembic et tests (en cours) ; déploiement plus tard

---

## 11. Commandes utiles

```bash
# Activer l'environnement virtuel
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\activate             # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur en dev
uvicorn app.main:app --reload

# Accès
# Site  : http://127.0.0.1:8000
# Docs  : http://127.0.0.1:8000/docs
# Redoc : http://127.0.0.1:8000/redoc

# Créer une migration
alembic revision --autogenerate -m "message"

# Appliquer les migrations
alembic upgrade head

# Lancer les tests
pytest