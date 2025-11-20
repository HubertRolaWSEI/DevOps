FROM python:3.10-slim

WORKDIR /app

# Kopiowanie i instalacja zależności (NOWY KROK)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie głównego pliku serwera (teraz kopiuje zaktualizowany server.py)
COPY server.py .

EXPOSE 8080

CMD ["python", "server.py"]

