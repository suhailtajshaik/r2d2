FROM python:3.11-slim

LABEL name="yoda" \
      description="Self-evolving VL-JEPA learning agent" \
      version="0.3"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create dirs for resources and knowledge persistence
RUN mkdir -p /app/resources /app/knowledge /app/checkpoints

# Entrypoint — default to status, override with any agent.py command
ENTRYPOINT ["python3", "agent.py"]
CMD ["status"]
