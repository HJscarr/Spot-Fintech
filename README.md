# FinServ Co - Internal API

**FinServ Co** is a financial services company managing customer accounts, transactions, and portfolio analytics through a monorepo-backed API platform.

## The Problem

We have **300+ open GitHub issues** across our monorepo. Most are small-to-medium bugs and feature requests that sit unresolved for months because senior engineers are focused on platform work. Junior engineers spend more time understanding issues than fixing them. We need a system that stops the bleeding.

## Tech Stack

- **Python 3.11+**
- **FastAPI** - REST API framework
- **SQLite** - Lightweight database (via SQLAlchemy)
- **Pydantic** - Data validation

## Project Structure

```
spot-fintech/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # Database connection and session management
│   └── routers/
│       ├── accounts.py   # Account CRUD endpoints
│       ├── transactions.py  # Transaction endpoints
│       └── portfolio.py  # Portfolio analytics endpoints
├── requirements.txt
└── README.md
```

## Getting Started

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Known Issues

This codebase has several open bugs tracked in GitHub Issues. See the Issues tab for details.
