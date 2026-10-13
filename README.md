# CleanHome — Backend

Plateforme de réservation de services de ménage à domicile.
Backend FastAPI + Jinja2.

Documentation technique complète : **[DOCUMENTATION.md](DOCUMENTATION.md)**.
Règles pour les contributeurs / agents IA : **[AGENTS.md](AGENTS.md)**.

## Stack

- FastAPI
- SQLAlchemy 2
- SQLite (dev)
- Jinja2 (templates HTML)
- JWT (auth)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate            # Windows

pip install -r requirements.txt
cp .env.example .env