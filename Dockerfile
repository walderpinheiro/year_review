FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/
COPY *.py .
COPY pytest.ini .

RUN mkdir -p /app/output /app/tokens

CMD ["python", "authenticate.py"]
