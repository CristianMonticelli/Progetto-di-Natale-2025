from app.db import get_db


def get_all_immobili():
    """Recupera tutti gli immobili con i loro coinquilini (LEFT JOIN)."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT '
            ' i.id AS immobile_id, i.via, i.civico, i.tipo_annuncio, i.photo, i.price_rent, i.price_sale, i.created AS immobile_created, i.author_id, u.username,'
            ' q.id AS coinquilino_id, q.nome AS coin_nome, q.cognome AS coin_cognome, q.email AS coin_email, q.numero_persone AS coin_numero_persone, q.eta AS coin_eta, q.created AS coin_created'
            ' FROM immobili i'
            ' JOIN user u ON i.author_id = u.id'
            ' LEFT JOIN coinquilini q ON q.immobile_id = i.id'
            ' ORDER BY i.created DESC, q.created ASC'
        ).fetchall()

        immobili = {}
        for r in rows:
            row = dict(r)
            iid = row.get('immobile_id')
            if iid not in immobili:
                immobili[iid] = {
                    'id': iid,
                    'via': row.get('via'),
                    'civico': row.get('civico'),
                    'tipo_annuncio': row.get('tipo_annuncio'),
                    'photo': row.get('photo'),
                    'price_rent': row.get('price_rent'),
                    'price_sale': row.get('price_sale'),
                    'created': row.get('immobile_created'),
                    'author_id': row.get('author_id'),
                    'username': row.get('username'),
                    'coinquilini': []
                }

            if row.get('coinquilino_id') is not None:
                immobili[iid]['coinquilini'].append({
                    'id': row.get('coinquilino_id'),
                    'nome': row.get('coin_nome'),
                    'cognome': row.get('coin_cognome'),
                    'email': row.get('coin_email'),
                    'numero_persone': row.get('coin_numero_persone'),
                    'eta': row.get('coin_eta'),
                    'created': row.get('coin_created')
                })

        return list(immobili.values())
    except Exception:
        return []


def get_user_immobili(user_id):
    """Recupera solo gli immobili di un utente specifico, con i coinquilini."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT '
            ' i.id AS immobile_id, i.via, i.civico, i.tipo_annuncio, i.photo, i.price_rent, i.price_sale, i.created AS immobile_created, i.author_id, u.username,'
            ' q.id AS coinquilino_id, q.nome AS coin_nome, q.cognome AS coin_cognome, q.email AS coin_email, q.numero_persone AS coin_numero_persone, q.eta AS coin_eta, q.created AS coin_created'
            ' FROM immobili i'
            ' JOIN user u ON i.author_id = u.id'
            ' LEFT JOIN coinquilini q ON q.immobile_id = i.id'
            ' WHERE i.author_id = ?'
            ' ORDER BY i.created DESC, q.created ASC',
            (user_id,)
        ).fetchall()

        immobili = {}
        for r in rows:
            row = dict(r)
            iid = row.get('immobile_id')
            if iid not in immobili:
                immobili[iid] = {
                    'id': iid,
                    'via': row.get('via'),
                    'civico': row.get('civico'),
                    'tipo_annuncio': row.get('tipo_annuncio'),
                    'photo': row.get('photo'),
                    'price_rent': row.get('price_rent'),
                    'price_sale': row.get('price_sale'),
                    'created': row.get('immobile_created'),
                    'author_id': row.get('author_id'),
                    'username': row.get('username'),
                    'coinquilini': []
                }
            if row.get('coinquilino_id') is not None:
                immobili[iid]['coinquilini'].append({
                    'id': row.get('coinquilino_id'),
                    'nome': row.get('coin_nome'),
                    'cognome': row.get('coin_cognome'),
                    'email': row.get('coin_email'),
                    'numero_persone': row.get('coin_numero_persone'),
                    'eta': row.get('coin_eta'),
                    'created': row.get('coin_created')
                })
        return list(immobili.values())
    except Exception:
        return []


def get_immobile_by_id(id):
    """Recupera un immobile specifico per ID, aggregando i coinquilini."""
    db = get_db()
    try:
        rows = db.execute(
            'SELECT '
            ' i.id AS immobile_id, i.via, i.civico, i.tipo_annuncio, i.photo, i.price_rent, i.price_sale, i.created AS immobile_created, i.author_id, u.username,'
            ' q.id AS coinquilino_id, q.nome AS coin_nome, q.cognome AS coin_cognome, q.email AS coin_email, q.numero_persone AS coin_numero_persone, q.eta AS coin_eta, q.created AS coin_created'
            ' FROM immobili i'
            ' JOIN user u ON i.author_id = u.id'
            ' LEFT JOIN coinquilini q ON q.immobile_id = i.id'
            ' WHERE i.id = ?'
            ' ORDER BY q.created ASC',
            (id,)
        ).fetchall()

        if not rows:
            return None

        immobile = None
        coinquilini = []
        for r in rows:
            row = dict(r)
            if immobile is None:
                immobile = {
                    'id': row.get('immobile_id'),
                    'via': row.get('via'),
                    'civico': row.get('civico'),
                    'tipo_annuncio': row.get('tipo_annuncio'),
                    'photo': row.get('photo'),
                    'price_rent': row.get('price_rent'),
                    'price_sale': row.get('price_sale'),
                    'created': row.get('immobile_created'),
                    'author_id': row.get('author_id'),
                    'username': row.get('username')
                }
            if row.get('coinquilino_id') is not None:
                coinquilini.append({
                    'id': row.get('coinquilino_id'),
                    'nome': row.get('coin_nome'),
                    'cognome': row.get('coin_cognome'),
                    'email': row.get('coin_email'),
                    'numero_persone': row.get('coin_numero_persone'),
                    'eta': row.get('coin_eta'),
                    'created': row.get('coin_created')
                })

        immobile['coinquilini'] = coinquilini
        return immobile
    except Exception:
        return None


def create_immobile(via, civico, author_id, tipo_annuncio='affitto', photo=None, price_rent=None, price_sale=None):
    """Crea un nuovo immobile nel database e ritorna il nuovo id."""
    db = get_db()
    try:
        cur = db.execute(
            'INSERT INTO immobili (via, civico, author_id, tipo_annuncio, photo, price_rent, price_sale)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?)',
            (via, civico, author_id, tipo_annuncio, photo, price_rent, price_sale)
        )
        db.commit()
        return db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    except Exception:
        return None


def update_immobile(id, via, civico, tipo_annuncio, photo=None, price_rent=None, price_sale=None):
    """Aggiorna un immobile esistente."""
    db = get_db()
    try:
        db.execute(
            'UPDATE immobili SET via = ?, civico = ?, tipo_annuncio = ?, photo = ?, price_rent = ?, price_sale = ?'
            ' WHERE id = ?',
            (via, civico, tipo_annuncio, photo, price_rent, price_sale, id)
        )
        db.commit()
        return True
    except:
        return False


def delete_immobile(id):
    """Elimina un immobile dal database."""
    db = get_db()
    try:
        db.execute('DELETE FROM immobili WHERE id = ?', (id,))
        db.commit()
        return True
    except:
        return False
