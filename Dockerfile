# Use Python slim image
FROM python:3.9-slim

WORKDIR /app

# 1. Install system packages early (doesn't change often)
RUN apt-get update && apt-get install -y \
    git \
    fonts-dejavu-core \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean

# 2. Copy only requirements first (cache this layer!)
COPY requirements.txt .

# 3. Install Python dependencies (cached unless requirements.txt changes)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install "dvc[aws]"

# 4. Now copy the rest of your code
COPY . .

# 5. Expose app
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]