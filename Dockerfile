# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential cmake wget && rm -rf /var/lib/apt/lists/*

# Install ttyd (latest release)
ADD https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 /usr/local/bin/ttyd
RUN chmod +x /usr/local/bin/ttyd

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Final image
FROM python:3.11-slim
COPY --from=builder /usr/local/bin/ttyd /usr/local/bin/ttyd
WORKDIR /app
COPY --from=builder /app /app
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose ttyd web port
EXPOSE 7681

# Default: run ttyd with your CLI
CMD ["ttyd", "python", "-m", "src.main"]
