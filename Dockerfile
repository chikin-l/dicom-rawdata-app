FROM python:3.12-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY app/*.py .
COPY app/config/config.json ./config/