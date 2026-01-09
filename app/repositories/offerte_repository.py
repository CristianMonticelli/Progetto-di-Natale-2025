from app.db import get_db

def create_offerta(immobile_id, user_id, nome, cognome, email, numero_telefono, messaggio):
    """Crea una nuova offerta/messaggio per un immobile."""
    db = get_db()
    try:
        cur = db.execute(
            'INSERT INTO offerte (immobile_id, user_id, nome, cognome, email, numero_telefono, messaggio)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?)',
            (immobile_id, user_id, nome, cognome, email, numero_telefono, messaggio)
        )
        db.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"Errore nell'inserimento offerta: {e}")
        return None

def get_offerte_by_immobile(immobile_id):
    """Recupera tutte le offerte per un immobile."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM offerte WHERE immobile_id = ? ORDER BY created DESC',
            (immobile_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    except:
        return []

def get_offerte_by_user(user_id):
    """Recupera tutte le offerte ricevute da un utente (proprietario)."""
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT o.*, i.via, i.civico 
               FROM offerte o
               JOIN immobili i ON o.immobile_id = i.id
               WHERE i.author_id = ?
               ORDER BY o.created DESC''',
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    except:
        return []

def get_offerta_by_id(offerta_id):
    """Recupera un'offerta per ID."""
    db = get_db()
    try:
        offerta = db.execute(
            'SELECT * FROM offerte WHERE id = ?',
            (offerta_id,)
        ).fetchone()
        return dict(offerta) if offerta else None
    except:
        return None

def get_offerte_sent_by_user(user_id):
    """Recupera tutte le offerte inviate da un offerente."""
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT o.*, i.via, i.civico, i.author_id
               FROM offerte o
               JOIN immobili i ON o.immobile_id = i.id
               WHERE o.user_id = ?
               ORDER BY o.created DESC''',
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    except:
        return []

def add_response(offerta_id, risposta_text):
    """Aggiunge una risposta (proprietario -> offerente) ad una offerta."""
    db = get_db()
    try:
        db.execute(
            'UPDATE offerte SET risposta = ?, risposta_created = CURRENT_TIMESTAMP, risposta_letta = 0 WHERE id = ?',
            (risposta_text, offerta_id)
        )
        db.commit()
        return True
    except Exception:
        return False

def mark_response_read(offerta_id):
    db = get_db()
    try:
        db.execute('UPDATE offerte SET risposta_letta = 1 WHERE id = ?', (offerta_id,))
        db.commit()
        return True
    except Exception:
        return False

def mark_as_read(offerta_id):
    """Marca un'offerta come letta."""
    db = get_db()
    try:
        db.execute(
            'UPDATE offerte SET read = 1 WHERE id = ?',
            (offerta_id,)
        )
        db.commit()
        return True
    except:
        return False

def delete_offerta(offerta_id):
    """Elimina un'offerta."""
    db = get_db()
    try:
        db.execute('DELETE FROM offerte WHERE id = ?', (offerta_id,))
        db.commit()
        return True
    except:
        return False

def count_unread_offerte(user_id):
    """Conta le offerte non lette per un utente."""
    db = get_db()
    try:
        result = db.execute(
            '''SELECT COUNT(*) as count FROM offerte o
               JOIN immobili i ON o.immobile_id = i.id
               WHERE i.author_id = ? AND o.read = 0''',
            (user_id,)
        ).fetchone()
        return result['count'] if result else 0
    except:
        return 0
