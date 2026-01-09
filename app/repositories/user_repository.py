# Importiamo la nostra funzione per prendere la connessione
from app.db import get_db

def create_user(username, email, password_hash, first_name='', last_name='', profile_photo=None, tipo_utente='proprietario'):
    """Inserisce un nuovo utente con nome, cognome e foto profilo opzionale."""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO user (username, email, password, first_name, last_name, profile_photo, tipo_utente) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, email, password_hash, first_name, last_name, profile_photo, tipo_utente),
        )
        db.commit() # Salviamo le modifiche
        return True
    except db.IntegrityError:
        # Errore: lo username esiste già
        return False


def update_user(user_id, username=None, email=None, first_name=None, last_name=None, profile_photo=None, password_hash=None):
    """Aggiorna i campi dell'utente. Solo i parametri non-None vengono aggiornati."""
    db = get_db()
    try:
        # Costruiamo query dinamica
        fields = []
        params = []
        if username is not None:
            fields.append('username = ?')
            params.append(username)
        if email is not None:
            fields.append('email = ?')
            params.append(email)
        if first_name is not None:
            fields.append('first_name = ?')
            params.append(first_name)
        if last_name is not None:
            fields.append('last_name = ?')
            params.append(last_name)
        if profile_photo is not None:
            fields.append('profile_photo = ?')
            params.append(profile_photo)
        if password_hash is not None:
            fields.append('password = ?')
            params.append(password_hash)

        if not fields:
            return True

        params.append(user_id)
        query = 'UPDATE user SET ' + ', '.join(fields) + ' WHERE id = ?'
        db.execute(query, tuple(params))
        db.commit()
        return True
    except Exception:
        return False

def get_user_by_username(username):
    """Cerca un utente per nome."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()
    return user

def get_user_by_id(user_id):
    """Cerca un utente per ID."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE id = ?", (user_id,)
    ).fetchone()
    return user