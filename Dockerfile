FROM python:3.11.4-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV TOKENIZERS_PARALLELISM=false

EXPOSE 7860

CMD ["python", "main.py"]