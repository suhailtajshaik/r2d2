FROM python:3.12-slim

RUN apt-get update && apt-get install -y docker.io curl openssl git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Claude Code CLI for Guardian/3PO repairs
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code

# Create r2d2 user matching host UID for 3PO calls
RUN groupadd -g 1000 r2d2 && useradd -u 1000 -g 1000 -m r2d2 && usermod -aG docker r2d2

COPY . .

CMD ["python3", "guardian.py"]
