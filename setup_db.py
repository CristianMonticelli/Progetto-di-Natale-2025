import sqlite3
import os
import json
from werkzeug.security import generate_password_hash

# Definiamo dove creare il file del database (nella cartella instance)
if not os.path.exists('instance'):
    os.makedirs('instance')

db_path = os.path.join('instance', 'gestionale.sqlite')

# Ci connettiamo (se il file non esiste, lo crea)
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row

# Leggiamo lo schema SQL
with open('app/schema.sql', encoding='utf-8') as f:
    connection.executescript(f.read())

# Carichiamo dati di esempio da app/seed.json (se presente)
seed_path = os.path.join('app', 'seed.json')
if os.path.exists(seed_path):
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed = json.load(f)

    cur = connection.cursor()

    # Inseriamo gli utenti
    for u in seed.get('users', []):
        try:
            hashed_pwd = generate_password_hash(u['password'])
            cur.execute(
                'INSERT INTO user (username, email, password, first_name, last_name, tipo_utente) VALUES (?, ?, ?, ?, ?, ?)',
                (u['username'], u.get('email', ''), hashed_pwd, u.get('first_name', ''), u.get('last_name', ''), u.get('tipo_utente', 'utente'))
            )
        except sqlite3.IntegrityError:
            # ignora utenti già presenti
            pass

    # Inseriamo gli immobili (usando username per trovare author_id)
    for c in seed.get('immobili', []):
        author = c.get('author_username') or c.get('author')
        if not author:
            continue
        cur.execute('SELECT id FROM user WHERE username = ?', (author,))
        row = cur.fetchone()
        if row:
            author_id = row[0]
            try:
                cur.execute(
                    'INSERT INTO immobili (author_id, via, civico, tipo_annuncio) VALUES (?, ?, ?, ?)',
                    (author_id, c['via'], c['civico'], c.get('tipo_annuncio', 'affitto'))
                )
            except sqlite3.IntegrityError:
                pass

    # Inseriamo i commenti/reviews
    for r in seed.get('reviews', []):
        # Troviamo l'immobile_id usando via e civico
        case_via = r.get('case_via')
        case_civico = r.get('case_civico')
        if not case_via or not case_civico:
            continue
        
        cur.execute('SELECT id FROM immobili WHERE via = ? AND civico = ?', (case_via, case_civico))
        case_row = cur.fetchone()
        if case_row:
            immobile_id = case_row[0]
            try:
                cur.execute(
                    'INSERT INTO reviews (immobile_id, reviewer_name, reviewer_email, rating, comment) VALUES (?, ?, ?, ?, ?)',
                    (immobile_id, r['reviewer_name'], r.get('reviewer_email'), r['rating'], r['comment'])
                )
            except sqlite3.IntegrityError:
                pass

    connection.commit()
    print("Dati di esempio caricati da:", seed_path)
else:
    print("Nessun seed trovato in:", seed_path)

print("Database creato con successo in:", db_path)
connection.close()