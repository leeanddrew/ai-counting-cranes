# Base image
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git ttf-dejavu-core && apt-get clean

# Copy code and model pointers
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install dvc[aws]

# Pull model only
RUN dvc pull models/best.pt.dvc --force

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
