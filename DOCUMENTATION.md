# CleanHome — Documentation technique

Document de référence de l’application telle qu’elle existe aujourd’hui.
Pour les règles à respecter en développement, voir aussi `AGENTS.md`.

---

## 1. Qu’est-ce que CleanHome ?

**CleanHome** est une plateforme web de **réservation de services de ménage à domicile**, ciblée Côte d’Ivoire (prix en **FCFA**).

Un particulier peut :

1. parcourir le catalogue de prestations ;
2. consulter le détail d’une prestation ;
3. créer un compte / se connecter ;
4. réserver (date + adresse + téléphone) ;
5. consulter ses réservations.

Un administrateur peut :

1. se connecter à un espace dédié ;
2. ajouter / supprimer des prestations ;
3. consulter toutes les réservations et changer leur statut.

**Aucun paiement en ligne.** Le client règle après l’intervention.

---

## 2. Périmètre

### Inclus

- Catalogue de ménage uniquement
- Comptes client et admin
- Réservations avec snapshot du prix
- Interface HTML (Jinja2) + API JSON `/api/v1` (préparée pour un futur mobile)

### Explicitement hors périmètre

Ne pas implémenter sans validation :

- Paiement (Wave, Orange Money, CB, Stripe, etc.)
- Avis, notation, commentaires
- Favoris, coupons, abonnements, portefeuille
- Chat, messagerie, notifications push
- Géolocalisation, carte, GPS
- Gestion RH / employés
- Tableaux de bord analytiques
- Marketplace multi-métiers
- Pages marketing (À propos, Blog, FAQ…)
- Connexion sociale (Google, Facebook, Apple)

---

## 3. Stack

| Couche | Choix |
|---|---|
| Langage | Python 3.11+ (éviter 3.14 si possible) |
| Web | FastAPI + Uvicorn |
| Templates | Jinja2 (pas de SPA, pas de React/Vue) |
| Front | HTML + CSS + JS vanilla |
| ORM | SQLAlchemy 2.x (`DeclarativeBase`) |
| Validation | Pydantic v2 |
| BDD | SQLite en développement (`cleanhome.db`) |
| Auth | JWT HS256, cookie `httponly` |
| Mots de passe | bcrypt via `passlib` (`bcrypt==4.0.1`) |
| Migrations | Alembic (`0001_initial`) |

**Non utilisés :** Django, Flask, Tailwind, Bootstrap, HTMX, Docker (pas encore).

---

## 4. Architecture

Architecture **en couches**. Une route ne contient ni SQL ni règle métier.

```
Requête HTTP
    → web/  (HTML)  ou  api/v1/  (JSON)
        → services/      (logique métier)
            → repositories/  (accès BDD)
                → models/    (tables SQLAlchemy)
```

| Dossier | Rôle |
|---|---|
| `app/web/` | Routes HTML (`TemplateResponse`) |
| `app/api/v1/` | Routes JSON |
| `app/services/` | Règles métier |
| `app/repositories/` | Requêtes SQLAlchemy |
| `app/models/` | Tables |
| `app/schemas/` | Schémas Pydantic |
| `app/core/` | JWT, `get_db`, gardes d’accès |
| `templates/` | Pages Jinja2 |
| `static/` | `css/cleanhome.css`, `js/cleanhome.js`, images |

Règle : une fonction de route reste courte ; la logique va dans un *service*.

---

## 5. Modèle de données

Trois tables.

### `users`

| Champ | Contraintes |
|---|---|
| `id` | PK |
| `full_name` | str(120), obligatoire |
| `email` | str(180), unique, indexé |
| `phone` | str(30) |
| `hashed_password` | str(255) |
| `is_admin` | bool, défaut `False` |
| `created_at` | datetime, auto |

**Un seul type de compte.** Deux rôles via `is_admin` :

- `False` → **client**
- `True` → **admin**

Le visiteur non connecté n’est pas stocké en base.

### `services` (prestations de ménage)

| Champ | Contraintes |
|---|---|
| `id` | PK |
| `name` | str(120) |
| `category` | str(80), indexé, **saisie libre** (pas d’enum) |
| `description` | texte |
| `price` | entier FCFA, `> 0` |
| `duration` | str(50), ex. `"3 heures"` |
| `image_url` | str(500), nullable |
| `created_at` | datetime, auto |

Modification via `/admin/services/{id}/edit`. Le prix des réservations déjà créées n’est pas recalculé.

### `bookings` (réservations)

| Champ | Contraintes |
|---|---|
| `id` | PK |
| `user_id` | FK → `users.id` |
| `service_id` | FK → `services.id` |
| `date` | date d’intervention |
| `address` | str(255) |
| `phone` | str(30) |
| `price` | **snapshot** du prix au moment de la réservation |
| `status` | voir ci-dessous |
| `created_at` | datetime, auto |

Statuts autorisés uniquement :

| Valeur | Libellé UI |
|---|---|
| `pending` | En attente (défaut à la création) |
| `confirmed` | Confirmée |
| `done` | Terminée |
| `cancelled` | Annulée |

Relations SQLAlchemy : `Booking.user` et `Booking.service` en `lazy="joined"`.

---

## 6. Authentification

- JWT HS256, payload `{ "sub": "<user_id>", "is_admin": <bool>, "exp": <ts> }`
- Cookie `access_token` : `httponly`, `samesite="lax"`
- Durée : 24 h (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`)
- Pas de refresh token, pas d’OAuth
- Le JWT n’est **jamais** mis en `localStorage`

### Pages HTML

- Non connecté sur une page client/admin → **303** vers `/login?next=...`
- Après login : retour sur `next` s’il s’agit d’un chemin local (`safe_next_url` bloque les URL externes)
- Client → `/reservations` par défaut ; admin → `/admin/services`
- Client qui ouvre `/admin/...` → **403**
- `/logout` supprime le cookie

### API JSON

Les gardes `require_user` / `require_admin` lisent **le même cookie**.  
`POST /api/v1/auth/login` renvoie `{ "access_token", "token_type": "bearer" }` mais les routes protégées ne lisent pas encore un header `Authorization`. Pour tester l’API authentifiée aujourd’hui : cookie de session HTML, ou évolution future (Bearer).

### Comptes de développement

Si `APP_ENV=development`, un admin est créé au démarrage s’il n’existe pas :

- Email : `admin@cleanhome.ci`
- Mot de passe : `admin123`

Ne pas utiliser ces identifiants en production.

---

## 7. Fonctionnement métier

### Catalogue

- Public. `GET /` liste toutes les prestations.
- Filtres de catégories côté **navigateur** (JS), pas en SQL.
- `GET /service/{id}` : 404 si introuvable.

### Inscription / connexion

- Mot de passe ≥ 6 caractères (schéma Pydantic).
- Confirmation de mot de passe côté page HTML.
- Email déjà pris → erreur « Un compte existe déjà… ».
- Identifiants faux → 400 HTML / 401 JSON.

### Réservation

1. Le client doit être connecté.
2. Date **≥ aujourd’hui**, adresse et téléphone non vides.
3. Le prix enregistré est celui de la prestation **au moment de la résa** (si l’admin change le tarif plus tard, les anciennes résas ne bougent pas).
4. Statut initial : `pending`.
5. Redirection vers `/confirmation/{id}`. Un client ne voit que **ses** réservations.

### Administration

- Ajout et **modification** de prestation (formulaire `multipart` : image PNG/JPG optionnelle → `static/img/services/`). Sans nouvelle image, l’existante est conservée.
- Suppression : refusée si des réservations y sont liées (contrainte FK).
- Changement de statut via `<select>` (soumission auto) sur `/admin/reservations`.

---

## 8. Routes HTML (`app/web/`)

| Méthode | URL | Auth | Rôle |
|---|---|---|---|
| GET | `/` | Public | Catalogue |
| GET | `/service/{id}` | Public | Détail |
| GET | `/login` | Public | Formulaire |
| POST | `/login` | Public | Connexion |
| GET | `/register` | Public | Formulaire |
| POST | `/register` | Public | Inscription |
| GET | `/logout` | Public | Déconnexion |
| GET | `/book/{service_id}` | Client | Formulaire résa |
| POST | `/book/{service_id}` | Client | Création résa |
| GET | `/confirmation/{booking_id}` | Client | Succès |
| GET | `/reservations` | Client | Mes réservations |
| GET | `/admin/services` | Admin | Liste prestations |
| GET | `/admin/services/new` | Admin | Formulaire ajout |
| POST | `/admin/services/new` | Admin | Création |
| GET | `/admin/services/{id}/edit` | Admin | Formulaire modification |
| POST | `/admin/services/{id}/edit` | Admin | Enregistrement |
| POST | `/admin/services/{id}/delete` | Admin | Suppression |
| GET | `/admin/reservations` | Admin | Toutes les résas |
| POST | `/admin/bookings/{id}/status` | Admin | Changement statut |

Erreurs HTML : le template est renvoyé avec `error` dans le contexte (pas de stack trace).

---

## 9. Routes JSON (`/api/v1`)

Préfixe : `/api/v1`. Docs Swagger : `/docs`, ReDoc : `/redoc`.

| Méthode | URL | Auth | Réponse |
|---|---|---|---|
| POST | `/auth/register` | Public | `Token` |
| POST | `/auth/login` | Public | `Token` |
| GET | `/services/` | Public | `ServiceOut[]` |
| GET | `/services/{id}` | Public | `ServiceOut` |
| GET | `/bookings/me` | Client | `BookingOut[]` |
| POST | `/bookings/` | Client | `BookingOut` (201) |
| GET | `/admin/bookings` | Admin | `BookingOut[]` |
| PATCH | `/admin/bookings/{id}/status` | Admin | `BookingOut` |
| POST | `/admin/services` | Admin | `ServiceOut` (201) |
| PUT | `/admin/services/{id}` | Admin | `ServiceOut` |
| DELETE | `/admin/services/{id}` | Admin | 204 |

Erreurs JSON : `HTTPException` avec `detail`.

---

## 10. Front

- Héritage Jinja : `templates/base.html` + `{% block title %}` / `content`
- Fragments : `partials/header.html`, `service_card.html`, `status_badge.html`
- CSS unique : `static/css/cleanhome.css`
- JS unique : `static/js/cleanhome.js` (filtres catalogue, filtres statut admin, aperçu upload, animations)
- Polices : **DM Sans** (corps), **Plus Jakarta Sans** (titres)
- Couleur principale : `--green-700: #087d6b`
- Animations respectent `prefers-reduced-motion`

Le header change selon l’état : visiteur / client / admin.

---

## 11. Configuration

Fichier `.env` (jamais commité). Copier `.env.example`.

| Variable | Rôle | Défaut |
|---|---|---|
| `DATABASE_URL` | Connexion SQLAlchemy | `sqlite:///./cleanhome.db` |
| `JWT_SECRET` | Signature JWT | à changer en prod |
| `JWT_ALGORITHM` | Algorithme | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée du token | `1440` |
| `APP_NAME` | Titre FastAPI | `CleanHome` |
| `APP_ENV` | `development` active le seed admin | `development` |

Accès uniquement via `app.config.settings` (pas `os.getenv` dans le métier).

En développement, `Base.metadata.create_all` crée les tables au boot.  
En production : `alembic upgrade head`.

---

## 12. Lancer le projet

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate
# Linux/macOS : source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --reload
```

- Site : http://127.0.0.1:8000
- Docs : http://127.0.0.1:8000/docs

```bash
pytest
alembic revision --autogenerate -m "message"
alembic upgrade head
```

Les tests utilisent `sqlite:///./test_cleanhome.db` et `APP_ENV=test` (pas de seed admin). Ils couvrent catalogue, auth, réservations et admin.

---

## 13. Flux utilisateur (résumé)

```
Visiteur
  → Catalogue → Détail
      → Réserver (si non connecté : /login?next=/book/{id})
          → Inscription ou connexion
              → Formulaire date / adresse / téléphone
                  → Confirmation
                      → Mes réservations

Admin
  → /login
      → Prestations (ajout / suppression)
      → Réservations (pending → confirmed → done | cancelled)
```

---

## 14. Limites connues / suite possible

- API JSON authentifiée via **cookie**, pas via `Authorization: Bearer`.
- CORS ouvert (`allow_origins=["*"]`) — à durcir avant une app mobile réelle.
- SQLite + `create_all` en dev ; PostgreSQL + Alembic prévus plus tard.
- Déploiement / Docker : pas encore dans le périmètre.
- `python-jose` émet des warnings `utcnow()` (dépendance, pas le code métier).

---

## 15. Fichiers à lire en priorité

| Fichier | Pourquoi |
|---|---|
| `AGENTS.md` | Contrat pour tout agent / contributeur |
| `app/main.py` | Assemblage de l’application |
| `app/core/dependencies.py` | Session, cookie JWT, gardes HTML vs API |
| `app/services/*.py` | Règles métier |
| `app/models/*.py` | Schéma de données |
| `templates/` | Pages visibles |
| `tests/` | Comportements attendus |

Ce document décrit l’état du code au Palier 6 (assemblage) + Palier 7 partiel (Alembic + tests). Le déploiement n’est pas documenté ici car il n’est pas implémenté.
