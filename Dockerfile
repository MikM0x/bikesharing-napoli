# Usa la versione ufficiale di Python, leggera e veloce
FROM python:3.11-slim

# Crea una cartella chiamata /app dentro la "scatola magica"
WORKDIR /app

# Copia il nostro file delle librerie
COPY app/requirements.txt .

# Fagli installare Flask e PyMongo
RUN pip install --no-cache-dir -r requirements.txt

# Ora copia TUTTO il nostro progetto dentro la scatola
COPY . .

# Diciamo a Docker che il sito uscirà dalla porta 5000
EXPOSE 5000

# Il comando per accendere il server!
CMD ["python", "app/app.py"]