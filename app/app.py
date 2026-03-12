import os
import random
from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Connessione al Database MongoDB
try:
    client = MongoClient("mongodb://db:27017/", serverSelectionTimeoutMS=2000)
    db = client.bikesharing
    collezione_stazioni = db.stazioni

    if collezione_stazioni.count_documents({}) == 0:
        stazioni_iniziali = [
            {"nome": "Stazione Centrale (Garibaldi)", "lat": 40.8528, "lng": 14.2721, "bici_disponibili": 5},
            {"nome": "Stazione Toledo", "lat": 40.8400, "lng": 14.2487, "bici_disponibili": 0},
            {"nome": "Piazza Plebiscito", "lat": 40.8358, "lng": 14.2486, "bici_disponibili": 12}
        ]
        collezione_stazioni.insert_many(stazioni_iniziali)

    client.server_info() 
    db_status = "🟢 Connesso a MongoDB"
except Exception as e:
    db_status = f"🔴 Errore DB: {e}"
    collezione_stazioni = None

# 1. Rotta Principale (La Mappa)
@app.route('/')
def home():
    stazioni_dal_db = []
    if collezione_stazioni is not None:
        stazioni_dal_db = list(collezione_stazioni.find({}, {"_id": 0}))
    return render_template('index.html', status=db_status, stazioni=stazioni_dal_db)

# 2. Rotta per Noleggiare
@app.route('/noleggia/<nome_stazione>')
def noleggia(nome_stazione):
    if collezione_stazioni is not None:
        stazione = collezione_stazioni.find_one({"nome": nome_stazione})
        if stazione and stazione["bici_disponibili"] > 0:
            collezione_stazioni.update_one(
                {"nome": nome_stazione},
                {"$inc": {"bici_disponibili": -1}} 
            )
    return redirect(url_for('home'))

# 3. Rotta per Restituire
@app.route('/restituisci/<nome_stazione>')
def restituisci(nome_stazione):
    if collezione_stazioni is not None:
        collezione_stazioni.update_one(
            {"nome": nome_stazione},
            {"$inc": {"bici_disponibili": 1}}
        )
    return redirect(url_for('home'))

# 4. NUOVA Rotta: Pagina di Dettaglio
@app.route('/stazione/<nome_stazione>')
def dettaglio_stazione(nome_stazione):
    if collezione_stazioni is not None:
        stazione = collezione_stazioni.find_one({"nome": nome_stazione})
        if stazione:
            capacita_massima = 15
            bici_presenti = stazione["bici_disponibili"]
            slot_vuoti = capacita_massima - bici_presenti if bici_presenti < capacita_massima else 0
            
            lista_mezzi = []
            for i in range(bici_presenti):
                if random.choice([True, False]):
                    lista_mezzi.append({
                        "tipo": "E-Bike",
                        "codice": f"#A{random.randint(10, 99)}",
                        "batteria": random.randint(40, 100),
                        "prezzo": "€0,25"
                    })
                else:
                    lista_mezzi.append({
                        "tipo": "Classic",
                        "codice": f"#B{random.randint(10, 99)}",
                        "prezzo": "€0,15"
                    })

            dati_schermata = {
                "nome": stazione["nome"],
                "posizione": "Napoli Centro", 
                "bici_disponibili": bici_presenti,
                "slot_disponibili": slot_vuoti,
                "immagine": "https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", 
                "mezzi": lista_mezzi
            }
            return render_template('dettaglio.html', stazione=dati_schermata)
            
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)