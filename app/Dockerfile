FROM python:3.13-slim-bookworm

ENV PROJECT_DIR="/app"

# Install system dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends --no-install-suggests -y \
       build-essential \
       libpq-dev \
       curl \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR $PROJECT_DIR

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv


# Copy project files
COPY . $PROJECT_DIR/

# Install dependencies via uv
RUN uv sync --no-dev

# Use a build argument for default port
ARG APP_PORT=8000
EXPOSE ${APP_PORT}

# Run FastAPI using shell and environment variable
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000}"
