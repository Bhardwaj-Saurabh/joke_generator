FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency definitions
COPY pyproject.toml .
# Copy lock file if it exists, otherwise it will be created
# COPY uv.lock . 

# Create virtual environment and install dependencies
RUN uv venv
RUN uv sync --frozen || uv sync

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
