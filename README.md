# FastAPI-Starter
A minimal and production-ready FastAPI project template to kickstart your next API.

It bundles sensible defaults for building asynchronous web services, including database
integration, background tasks, and authentication, so you can focus on shipping features
instead of wiring boilerplate.

## Features

- FastAPI application with a structured project layout
- Asynchronous database support via SQLAlchemy and PostgreSQL
- Docker and Docker Compose setup for local development
- Authentication scaffolding with JWT tokens and rate limiting
- Environment-based settings ready for deployment

## Getting Started

### Prerequisites

- Python 3.13
- [uv](https://github.com/astral-sh/uv) for dependency management and task running
- Docker and Redis (optional) for running supporting services

### Installation

```bash
git clone https://github.com/<azizjon-aliev>/fastapi-starter.git
cd fastapi-starter
uv sync
```

### Usage

Run the application with `uv`:

```bash
uv run app/main.py
```

Or start with Uvicorn directly:

```bash
uv run uvicorn app.main:app --reload
```

Once running, visit `http://localhost:8000/docs` for interactive Swagger UI.

Available API endpoints:

- `POST /api/v1/auth/login` – obtain access and refresh tokens
- `POST /api/v1/auth/register` – create a new user
- `POST /api/v1/auth/refresh-token` – refresh expired tokens
- `POST /api/v1/users/me` – retrieve the currently authenticated user

## Demo

![Demo Screenshot](...LINK)

The screenshot above shows the interactive API documentation accessible at
`http://localhost:8000/docs`. Submitting a `POST` to `/api/v1/auth/login` with valid
credentials returns a JWT access token.

## Contributing

1. Fork the repository and clone your fork
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dependencies and run linters: `uv sync` and `uv run ruff check .`
4. Commit your changes and push the branch
5. Open a pull request describing your changes

## License

This project is licensed under the [MIT License](LICENSE).

