from app.db import get_db

def create_review(immobile_id, reviewer_name, rating, comment=None, reviewer_email=None):
    """Crea un nuovo commento/valutazione anonimo sull'immobile."""
    db = get_db()
    try:
        db.execute(
            'INSERT INTO reviews (immobile_id, reviewer_name, reviewer_email, rating, comment) VALUES (?, ?, ?, ?, ?)',
            (immobile_id, reviewer_name, reviewer_email, rating, comment)
        )
        db.commit()
        return db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    except Exception as e:
        print(f"Errore nella creazione review: {e}")
        return None


def get_review_by_id(review_id):
    """Recupera una review per ID."""
    db = get_db()
    try:
        review = db.execute(
            'SELECT * FROM reviews WHERE id = ?',
            (review_id,)
        ).fetchone()
        return dict(review) if review else None
    except Exception:
        return None


def get_reviews_for_immobile(immobile_id):
    """Recupera tutte le reviews per un immobile."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM reviews WHERE immobile_id = ? ORDER BY created DESC',
            (immobile_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_average_rating_for_immobile(immobile_id):
    """Calcola la valutazione media per un immobile."""
    db = get_db()
    try:
        result = db.execute(
            'SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE immobile_id = ?',
            (immobile_id,)
        ).fetchone()
        if result and result['count'] > 0:
            return {
                'average': round(result['avg_rating'], 2),
                'count': result['count']
            }
        return None
    except Exception:
        return None


def add_owner_response(review_id, response_text):
    """Aggiunge una risposta del proprietario a un commento."""
    db = get_db()
    try:
        db.execute(
            'UPDATE reviews SET owner_response = ?, owner_response_created = CURRENT_TIMESTAMP WHERE id = ?',
            (response_text, review_id)
        )
        db.commit()
        return True
    except Exception:
        return False


def update_review(review_id, rating=None, comment=None):
    """Aggiorna un commento (solo rating e comment, anonimamente)."""
    db = get_db()
    try:
        fields = []
        params = []
        if rating is not None:
            fields.append('rating = ?')
            params.append(rating)
        if comment is not None:
            fields.append('comment = ?')
            params.append(comment)
        
        if not fields:
            return True
        
        fields.append('updated = CURRENT_TIMESTAMP')
        params.append(review_id)
        query = 'UPDATE reviews SET ' + ', '.join(fields) + ' WHERE id = ?'
        db.execute(query, tuple(params))
        db.commit()
        return True
    except Exception:
        return False


def delete_review(review_id):
    """Elimina un commento."""
    db = get_db()
    try:
        db.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
        db.commit()
        return True
    except Exception:
        return False


def get_reviews_for_owner(owner_id):
    """Recupera tutte le reviews ricevute dal proprietario (sui suoi immobili)."""
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT r.*, i.via, i.civico, i.id as immobile_id
               FROM reviews r
               JOIN immobili i ON r.immobile_id = i.id
               WHERE i.author_id = ?
               ORDER BY r.created DESC''',
            (owner_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
