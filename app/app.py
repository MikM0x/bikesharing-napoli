import os
from flask import Flask, render_template
from pymongo import MongoClient

# 1. Configurazione Cartelle
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# 2. Connessione al Database MongoDB
# NOTA MAGICA: Invece di 'localhost', usiamo 'db' che è il nome del container nel docker-compose!
try:
    client = MongoClient("mongodb://db:27017/", serverSelectionTimeoutMS=2000)
    # Facciamo un test per vedere se risponde
    client.server_info() 
    db_status = "🟢 Connesso a MongoDB con successo!"
except Exception as e:
    db_status = f"🔴 Errore di connessione al database: {e}"

# 3. La nostra rotta principale
@app.route('/')
def home():
    # Passiamo lo stato del database alla pagina HTML
    return render_template('index.html', status=db_status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)