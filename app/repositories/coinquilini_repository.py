from app.db import get_db




def get_coinquilini_by_immobile(immobile_id):
    """Recupera tutti i coinquilini di un immobile."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM coinquilini WHERE immobile_id = ? ORDER BY created DESC',
            (immobile_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    except:
        return []


def get_coinquilino_by_id(id):
    """Recupera un coinquilino per ID."""
    db = get_db()
    try:
        coinquilino = db.execute(
            'SELECT * FROM coinquilini WHERE id = ?',
            (id,)
        ).fetchone()
        return dict(coinquilino) if coinquilino else None
    except:
        return None


def get_coinquilini_by_email(email):
    """Recupera tutti i coinquilini che hanno questa email."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM coinquilini WHERE email = ? ORDER BY created ASC',
            (email,)
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def create_coinquilino(immobile_id, nome, cognome, email, importo, giorno, numero_persone=None, eta=None):
    """Crea un nuovo coinquilino con dati di pagamento."""
    db = get_db()
    try:
        cur = db.execute(
            'INSERT INTO coinquilini (immobile_id, nome, cognome, email, importo, giorno, numero_persone, eta)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (immobile_id, nome, cognome, email, importo, giorno, numero_persone, eta)
        )
        db.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"Errore nell'inserimento coinquilino: {e}")
        return None


def update_coinquilino(id, nome, cognome, email, importo, giorno, numero_persone=None, eta=None):
    """Aggiorna un coinquilino con i dati di pagamento."""
    db = get_db()
    try:
        db.execute(
            'UPDATE coinquilini SET nome = ?, cognome = ?, email = ?, importo = ?, giorno = ?, numero_persone = ?, eta = ?'
            ' WHERE id = ?',
            (nome, cognome, email, importo, giorno, numero_persone, eta, id)
        )
        db.commit()
        return True
    except:
        return False


def delete_coinquilino(id):
    """Elimina un coinquilino."""
    db = get_db()
    try:
        db.execute('DELETE FROM coinquilini WHERE id = ?', (id,))
        db.commit()
        return True
    except:
        return False

def update_last_sent(id, last_sent):
    """Aggiorna la data di ultimo invio per un coinquilino."""
    db = get_db()
    try:
        db.execute(
            'UPDATE coinquilini SET last_sent = ? WHERE id = ?',
            (last_sent, id)
        )
        db.commit()
        return True
    except:
        return False


def get_due_coinquilini_by_day(day):
    """Recupera tutti i coinquilini il cui campo `giorno` == day.

    Restituisce una lista di dict che includono i campi del coinquilino
    e informazioni sull'immobile e sull'autore (username, author_id).
    """
    db = get_db()
    try:
        rows = db.execute(
            'SELECT q.*, i.via, i.civico, i.author_id, u.username AS author_username'
            ' FROM coinquilini q'
            ' JOIN immobili i ON q.immobile_id = i.id'
            ' JOIN user u ON i.author_id = u.id'
            ' WHERE q.giorno = ?'
            ' ORDER BY q.id ASC',
            (day,)
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
