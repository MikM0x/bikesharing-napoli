import os
import random
from flask import Flask, render_template, redirect, url_for, session
from pymongo import MongoClient

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "chiave_segreta_esame" 

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

@app.route('/')
def home():
    # MAGIA: Se sei in sella, il sito ti sbatte direttamente sulla nuova schermata!
    if session.get('in_corsa', False):
        return redirect(url_for('corsa_attiva'))

    stazioni_dal_db = []
    if collezione_stazioni is not None:
        stazioni_dal_db = list(collezione_stazioni.find({}, {"_id": 0}))
    return render_template('index.html', status=db_status, stazioni=stazioni_dal_db)

@app.route('/noleggia/<nome_stazione>')
def noleggia(nome_stazione):
    if collezione_stazioni is not None:
        stazione = collezione_stazioni.find_one({"nome": nome_stazione})
        if stazione and stazione["bici_disponibili"] > 0:
            collezione_stazioni.update_one({"nome": nome_stazione}, {"$inc": {"bici_disponibili": -1}})
            session['in_corsa'] = True # Memorizziamo che stai pedalando
    return redirect(url_for('home'))

# NUOVA ROTTA: La schermata che hai progettato
@app.route('/corsa_attiva')
def corsa_attiva():
    if not session.get('in_corsa', False):
        return redirect(url_for('home'))
    return render_template('corsa_attiva.html')

# NUOVA ROTTA: La schermata dello scontrino finale
@app.route('/fine_corsa')
def fine_corsa():
    # Qui in futuro passeremo i dati veri della corsa (tempo reale, costo reale)
    # Per ora creiamo un prototipo visivo!
    return render_template('fine_corsa.html')

@app.route('/segnala_problema')
def segnala_problema():
    # Per ora mostriamo solo il prototipo visivo
    # In futuro qui passeremo l'ID della bici e della corsa
    return render_template('segnala_problema.html')

@app.route('/termina_corsa')
def termina_corsa():
    session['in_corsa'] = False # Hai parcheggiato!
    return redirect(url_for('home'))

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
                    lista_mezzi.append({"tipo": "E-Bike", "codice": f"#A{random.randint(10, 99)}", "batteria": random.randint(40, 100), "prezzo": "€0,25"})
                else:
                    lista_mezzi.append({"tipo": "Classic", "codice": f"#B{random.randint(10, 99)}", "prezzo": "€0,15"})

            dati_schermata = {"nome": stazione["nome"], "posizione": "Napoli Centro", "bici_disponibili": bici_presenti, "slot_disponibili": slot_vuoti, "immagine": "https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "mezzi": lista_mezzi}
            return render_template('dettaglio.html', stazione=dati_schermata)
    return redirect(url_for('home'))

# NUOVA ROTTA: Pagina di Login
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registrati')
def registrati():
    return render_template('registrati.html')

# Wallet e Abbonamenti (I Miei Piani)
@app.route('/piani')
def piani():
    return render_template('piani.html')

@app.route('/profilo')
def profilo():
    return render_template('profilo.html')
# --- SOTTO-PAGINE DEL PROFILO ---
@app.route('/modifica_dati')
def modifica_dati():
    return render_template('modifica_dati.html')

@app.route('/notifiche')
def notifiche():
    return render_template('notifiche.html')

@app.route('/supporto')
def supporto():
    return render_template('supporto.html')

# La Cronologia delle Corse
@app.route('/corse')
def corse():
    return render_template('corse.html')

# Dashboard Segreta del Manutentore
@app.route('/manutentore')
def manutentore():
    return render_template('manutentore.html')

# Dashboard Admin (Gestore da PC)
@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)