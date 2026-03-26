FROM python:3.11-slim

# Work directory inside container
WORKDIR /app

# Install system deps (optional, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script
COPY build_stocks_timeline.py .

# Default command: run the script
CMD ["python", "build_stocks_timeline.py"]
