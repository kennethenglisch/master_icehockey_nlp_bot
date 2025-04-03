# Verwende ein leichtgewichtiges Python-Image
FROM python:3.12.0

# Setze das Arbeitsverzeichnis im Container
WORKDIR /

# Kopiere ausschließlich die gewünschten Ordner und deren Inhalte in den Container
COPY data/json/ ./data/json/
COPY data/roberta/embeddings/ ./data/roberta/embeddings/
COPY src/rulebot/ ./src/rulebot/

# Kopiere die Abhängigkeitsliste (requirements.txt) in das Arbeitsverzeichnis
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu124


# Spacy Modell installieren
RUN python -m spacy download en_core_web_sm

# Kopiere den restlichen Quellcode in den Container
#COPY . .

# Exponiere den Port (z. B. 8000), auf dem deine FastAPI-Anwendung läuft
EXPOSE 8000

# Starte den Server über uvicorn
# Starte die Anwendung mit korrekt gesetztem Python-Pfad
ENV PYTHONPATH=/src
CMD ["uvicorn", "src.rulebot.api:app", "--host", "0.0.0.0", "--port", "8000"]
