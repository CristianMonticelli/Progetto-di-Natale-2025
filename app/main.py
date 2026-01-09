import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from werkzeug.exceptions import abort
from app.repositories import immobile_repository, coinquilini_repository, offerte_repository, review_repository, user_repository
from app.notifications import check_and_send_reminders, send_welcome_email
from app.file_utils import allowed_file, generate_saved_filename

# Usiamo 'main' perché è il blueprint principale del sito
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Controlla e invia reminders di pagamento
    check_and_send_reminders()
    
    # Recupera il filtro dal query parameter
    tipo_filtro = request.args.get('tipo', 'tutti')
    
    # Se sei loggato come utente: se sei offerente mostra tutte gli immobili,
    # altrimenti (proprietario) mostra solo i tuoi immobili
    if g.user is None:
        immobili = immobile_repository.get_all_immobili()
    else:
        if g.user.get('tipo_utente') == 'offerente':
            immobili = immobile_repository.get_all_immobili()
        else:
            immobili = immobile_repository.get_user_immobili(g.user['id'])
    
    # Applica il filtro e nascondi immobili occupati (a meno che non sia l'offerente)
    if tipo_filtro != 'tutti':
        # Se l'immobile è "affitto/vendita" rientra sia in affitto che in vendita
        immobili = [i for i in immobili if i.get('tipo_annuncio') == tipo_filtro or i.get('tipo_annuncio') == 'affitto/vendita']
    else:
        # Se sei offerente, vedi tutto; altrimenti nascondi immobili occupati
        if g.user is not None and g.user.get('tipo_utente') != 'offerente':
            immobili = [i for i in immobili if i.get('tipo_annuncio') != 'occupata']
    
    # Recupera i coinquilini per ogni immobile e li allega al record
    for immobile in immobili:
        try:
            immobile['coinquilini'] = coinquilini_repository.get_coinquilini_by_immobile(immobile['id'])
        except Exception:
            immobile['coinquilini'] = []

    return render_template('index.html', immobili=immobili, tipo_filtro=tipo_filtro)

@bp.route('/about')
def about():
    return render_template('about.html')

# --- NUOVA ROUTE: CREAZIONE IMMOBILE ---
@bp.route('/create', methods=('GET', 'POST'))
def create():
    # Protezione: Se non sei loggato, vai al login
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))

    if request.method == 'POST':
        via = request.form['via']
        civico = request.form['civico']
        tipo_annuncio = request.form.get('tipo_annuncio', 'affitto')
        # Prezzi (possono essere vuoti)
        price_rent = request.form.get('price_rent') or None
        price_sale = request.form.get('price_sale') or None
        # Gestione upload foto
        photo_file = request.files.get('photo')
        photo_filename = None
        if photo_file and photo_file.filename:
            if allowed_file(photo_file.filename):
                filename = generate_saved_filename(photo_file.filename, prefix=via.replace(' ', '_'))
                photo_filename = filename
                upload_folder = current_app.config.get('UPLOAD_FOLDER')
                if upload_folder:
                    try:
                        os.makedirs(upload_folder, exist_ok=True)
                    except Exception:
                        pass
                    photo_file.save(os.path.join(upload_folder, photo_filename))
        error = None

        if not via:
            error = 'La via è obbligatoria.'

        if error is not None:
            flash(error)
        else:
            # Creiamo l'immobile usando l'ID dell'utente loggato (g.user['id'])
            new_id = immobile_repository.create_immobile(via, civico, g.user['id'], tipo_annuncio, photo=photo_filename, price_rent=price_rent, price_sale=price_sale)
            if new_id:
                flash(f'Proprietà registrata con successo!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Errore: il database non è inizializzato. Contatta l\'amministratore.', 'error')
                return redirect(url_for('main.create'))

    return render_template('crud_case/create.html')

def get_immobile(id, check_author=True):
    # 1. Recupera l'immobile dal DB
    immobile = immobile_repository.get_immobile_by_id(id)

    # 2. Se non esiste -> Errore 404 Not Found
    if immobile is None:
        abort(404, f"L'immobile id {id} non esiste.")

    # 3. Controllo AUTORIZZAZIONE
    # Se check_author è attivo, controlla che l'autore sia l'utente loggato
    if check_author and immobile['author_id'] != g.user['id']:
        abort(403) # Errore 403 Forbidden (Vietato!)

    return immobile

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    # --- LIVELLO 1: PROTEZIONE (Sei loggato?) ---
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))
    
    # --- LIVELLO 2: AUTORIZZAZIONE (È tuo?) ---
    # Questa funzione blocca tutto con un errore 403 se l'immobile non è tuo
    immobile = get_immobile(id)

    if request.method == 'POST':
        via = request.form['via']
        civico = request.form['civico']
        tipo_annuncio = request.form.get('tipo_annuncio', 'affitto')
        # Prezzi e foto
        price_rent = request.form.get('price_rent') or None
        price_sale = request.form.get('price_sale') or None
        photo_file = request.files.get('photo')
        photo_filename = immobile.get('photo')
        if photo_file and photo_file.filename:
            if allowed_file(photo_file.filename):
                filename = generate_saved_filename(photo_file.filename, prefix=via.replace(' ', '_'))
                photo_filename = filename
                upload_folder = current_app.config.get('UPLOAD_FOLDER')
                if upload_folder:
                    try:
                        os.makedirs(upload_folder, exist_ok=True)
                    except Exception:
                        pass
                    photo_file.save(os.path.join(upload_folder, photo_filename))
        error = None

        if not via:
            error = 'La via è obbligatoria.'

        if error is not None:
            flash(error)
        else:
            success = immobile_repository.update_immobile(id, via, civico, tipo_annuncio, photo=photo_filename, price_rent=price_rent, price_sale=price_sale)
            if success:
                flash(f'Proprietà aggiornata con successo!', 'success')
            else:
                flash('Errore nell\'aggiornamento della proprietà.', 'error')
            return redirect(url_for('main.index'))

    return render_template('crud_case/update.html', case=immobile)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    # 1. Sei loggato?
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))
    
    # 2. È tuo?
    get_immobile(id) 
    
    # 3. Cancella
    success = immobile_repository.delete_immobile(id)
    if success:
        flash('Proprietà eliminata con successo!', 'success')
    else:
        flash('Errore nell\'eliminazione della proprietà.', 'error')
    return redirect(url_for('main.index'))


@bp.route('/<int:immobile_id>/coinquilini/add', methods=('GET', 'POST'))
def add_coinquilino(immobile_id):
    # Protezione: Sei loggato?
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))
    
    # Verifica che l'immobile esista e sia tuo (check_author=True per verificare autorizzazione)
    immobile = get_immobile(immobile_id, check_author=True)
    
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        importo = request.form.get('importo')
        giorno = request.form.get('giorno')
        numero_persone = request.form.get('numero_persone')
        eta = request.form.get('eta')

        error = None
        if not nome:
            error = 'Nome obbligatorio.'
        elif not cognome:
            error = 'Cognome obbligatorio.'
        elif not email:
            error = 'Email obbligatoria.'
        elif not importo:
            error = 'Importo obbligatorio.'
        elif not giorno:
            error = 'Giorno obbligatorio.'

        if error is not None:
            flash(error, 'error')
        else:
            # Validate and convert
            try:
                importo = float(importo)
            except Exception:
                flash('Importo non valido.', 'error')
                return render_template('coinquilini/add_coinquilino.html', case=immobile)
            try:
                giorno = int(giorno)
                if not (1 <= giorno <= 28):
                    raise ValueError()
            except Exception:
                flash('Giorno deve essere un numero tra 1 e 28.', 'error')
                return render_template('coinquilini/add_coinquilino.html', case=immobile)

            # Converti a numeri o None
            numero_persone = int(numero_persone) if numero_persone and numero_persone.strip() else None

            new_id = coinquilini_repository.create_coinquilino(
                immobile_id, nome, cognome, email, importo, giorno, numero_persone, eta
            )
            if new_id:
                # Invia email di benvenuto con le informazioni di pagamento
                send_welcome_email(
                    coinquilino_nome=nome,
                    coinquilino_email=email,
                    importo=importo,
                    giorno=giorno,
                    case_via=immobile['via'],
                    case_civico=immobile['civico'],
                    sender_name=(g.user.get('first_name','') + ' ' + g.user.get('last_name','')).strip(),
                    sender_email=g.user.get('email')
                )
                flash('Coinquilino aggiunto con successo!', 'success')
                return redirect(url_for('main.view_case', case_id=immobile_id))
            else:
                flash('Errore nell\'aggiunta del coinquilino.', 'error')
    
    return render_template('coinquilini/add_coinquilino.html', case=immobile)


@bp.route('/coinquilino/<int:coinquilino_id>/edit', methods=('GET', 'POST'))
def edit_coinquilino(coinquilino_id):
    # Protezione: Sei loggato?
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))
    
    # Recupera il coinquilino
    coinquilino = coinquilini_repository.get_coinquilino_by_id(coinquilino_id)
    if coinquilino is None:
        abort(404)
    
    # Verifica che l'immobile sia tuo
    immobile = immobile_repository.get_immobile_by_id(coinquilino['immobile_id'])
    if immobile['author_id'] != g.user['id']:
        abort(403)
    
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        importo = request.form.get('importo')
        giorno = request.form.get('giorno')
        numero_persone = request.form.get('numero_persone')
        eta = request.form.get('eta')

        error = None
        if not nome:
            error = 'Nome obbligatorio.'
        elif not cognome:
            error = 'Cognome obbligatorio.'
        elif not email:
            error = 'Email obbligatoria.'
        elif not importo:
            error = 'Importo obbligatorio.'
        elif not giorno:
            error = 'Giorno obbligatorio.'

        if error is not None:
            flash(error, 'error')
        else:
            # Validate and convert
            try:
                importo = float(importo)
            except Exception:
                flash('Importo non valido.', 'error')
                return render_template('coinquilini/edit_coinquilino.html', coinquilino=coinquilino)
            try:
                giorno = int(giorno)
                if not (1 <= giorno <= 28):
                    raise ValueError()
            except Exception:
                flash('Giorno deve essere un numero tra 1 e 28.', 'error')
                return render_template('coinquilini/edit_coinquilino.html', coinquilino=coinquilino)

            # Converti a numeri o None
            numero_persone = int(numero_persone) if numero_persone else None
            eta = int(eta) if eta else None

            success = coinquilini_repository.update_coinquilino(
                coinquilino_id, nome, cognome, email, importo, giorno, numero_persone, eta
            )
            if success:
                flash(f'Coinquilino aggiornato con successo!', 'success')
                return redirect(url_for('main.view_case', case_id=coinquilino['immobile_id']))
            else:
                flash('Errore nell\'aggiornamento del coinquilino.', 'error')
    
    return render_template('coinquilini/edit_coinquilino.html', coinquilino=coinquilino)


@bp.route('/<int:case_id>/view')
def view_case(case_id):
    # Recupera l'immobile
    immobile = immobile_repository.get_immobile_by_id(case_id)
    if immobile is None:
        abort(404)
    
    # Recupera i coinquilini
    coinquilini = coinquilini_repository.get_coinquilini_by_immobile(case_id)
    
    # Se l'utente è il proprietario, mostra le chiavi di accesso
    show_keys = g.user is not None and g.user['id'] == immobile.get('author_id')
    
    return render_template('crud_case/view_case.html', case=immobile, coinquilini=coinquilini, show_keys=show_keys)


@bp.route('/coinquilino/<int:coinquilino_id>/delete', methods=('POST',))
def delete_coinquilino(coinquilino_id):
    # Protezione: Sei loggato?
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))
    
    # Recupera il coinquilino
    coinquilino = coinquilini_repository.get_coinquilino_by_id(coinquilino_id)
    if coinquilino is None:
        abort(404)
    
    # Verifica che l'immobile sia tuo
    immobile = immobile_repository.get_immobile_by_id(coinquilino['immobile_id'])
    if immobile['author_id'] != g.user['id']:
        abort(403)
    
    # Elimina
    success = coinquilini_repository.delete_coinquilino(coinquilino_id)
    if success:
        flash('Coinquilino eliminato con successo!', 'success')
    else:
        flash('Errore nell\'eliminazione del coinquilino.', 'error')
    
    return redirect(url_for('main.view_case', case_id=coinquilino['immobile_id']))


# --- ROUTE PER LE OFFERTE ---
@bp.route('/<int:immobile_id>/offerta', methods=('GET', 'POST'))
def send_offerta(immobile_id):
    """Invia un'offerta/messaggio al proprietario di un immobile."""
    immobile = immobile_repository.get_immobile_by_id(immobile_id)
    if immobile is None:
        abort(404)
    
    # Se NON sei loggato, reindirizza al login
    if g.user is None:
        flash('Devi essere loggato come OFFERENTE per inviare offerte.', 'warning')
        return redirect(url_for('auth.loginEregister'))
    
    # Se sei loggato ma non sei un offerente, blocca
    if g.user.get('tipo_utente') != 'offerente':
        flash('Solo gli OFFERENTI possono inviare offerte. Il tuo account è di tipo: ' + g.user.get('tipo_utente', 'sconosciuto'), 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Use account information from logged-in user; form no longer asks nome/cognome/email
        numero_telefono = request.form.get('numero_telefono')
        messaggio = request.form.get('messaggio')

        error = None
        if not messaggio:
            error = 'Messaggio obbligatorio.'

        if error is not None:
            flash(error, 'error')
        else:
            nome = g.user.get('username') or ''
            cognome = ''
            email = g.user.get('email') or ''
            offerta_id = offerte_repository.create_offerta(
                immobile_id, g.user['id'], nome, cognome, email, numero_telefono, messaggio
            )
            
            if offerta_id:
                flash('Offerta inviata con successo! Il proprietario riceverà il tuo messaggio.', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Errore nell\'invio dell\'offerta.', 'error')
    
    return render_template('offerta/send_offerta.html', case=immobile)


@bp.route('/offerte')
def offerte():
    """Mostra tutte le offerte ricevute dall'utente (proprietario)."""
    if g.user is None:
        return redirect(url_for('auth.registerElogin'))
    
    offerte_list = offerte_repository.get_offerte_by_user(g.user['id'])
    
    # Marca tutte le offerte come lette
    for offerta in offerte_list:
        if not offerta.get('read'):
            offerte_repository.mark_as_read(offerta['id'])
        # Aggiungi immagine profilo del mittente (se esiste)
        try:
            sender = user_repository.get_user_by_id(offerta.get('user_id'))
            sender = dict(sender) if sender is not None else None
            offerta['sender_profile'] = sender.get('profile_photo') if sender else None
            offerta['sender_username'] = sender.get('username') if sender else offerta.get('nome')
        except Exception:
            offerta['sender_profile'] = None
            offerta['sender_username'] = offerta.get('nome')
    
    return render_template('offerta/offerte.html', offerte=offerte_list)


@bp.route('/offerte/inviate')
def offerte_inviate():
    """Mostra le offerte inviate dall'utente (offerente) e le eventuali risposte."""
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))

    # Solo offerenti possono vedere le offerte inviate
    if g.user.get('tipo_utente') != 'offerente':
        flash('Solo gli offerenti possono vedere le offerte inviate.', 'error')
        return redirect(url_for('main.index'))

    offerte_list = offerte_repository.get_offerte_sent_by_user(g.user['id'])

    # Marca risposte come lette quando l'offerente visita la pagina
    for offerta in offerte_list:
        if offerta.get('risposta') and not offerta.get('risposta_letta'):
            offerte_repository.mark_response_read(offerta['id'])
        # Aggiungi immagine profilo del proprietario della casa
        try:
            immobile = immobile_repository.get_immobile_by_id(offerta.get('immobile_id'))
            owner = user_repository.get_user_by_id(immobile.get('author_id')) if immobile else None
            owner = dict(owner) if owner is not None else None
            offerta['owner_profile'] = owner.get('profile_photo') if owner else None
            offerta['owner_username'] = owner.get('username') if owner else None
        except Exception:
            offerta['owner_profile'] = None
            offerta['owner_username'] = None

    return render_template('offerta/offerte_inviate.html', offerte=offerte_list)


@bp.route('/offerta/<int:offerta_id>/respond', methods=('GET', 'POST'))
def respond_offerta(offerta_id):
    """Permette al proprietario dell'immobile di rispondere ad una offerta."""
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))

    offerta = offerte_repository.get_offerta_by_id(offerta_id)
    if offerta is None:
        abort(404)

    # Verifica che l'utente sia il proprietario dell'immobile relativo all'offerta
    immobile = immobile_repository.get_immobile_by_id(offerta['immobile_id'])
    if immobile['author_id'] != g.user['id']:
        abort(403)

    if request.method == 'POST':
        risposta = request.form.get('risposta')
        if not risposta:
            flash('La risposta non può essere vuota.', 'error')
        else:
            success = offerte_repository.add_response(offerta_id, risposta)
            if success:
                # Invia anche una notifica via email all'offerente
                try:
                    from app.notifications import send_reply_notification
                    # offerta contiene email del offerente
                    send_reply_notification(offerta.get('email'), g.user.get('username'), immobile['via'], risposta)
                except Exception:
                    pass

                flash('Risposta inviata all\'offerente e notificata.', 'success')
                return redirect(url_for('main.offerte'))
            else:
                flash('Errore nell\'invio della risposta.', 'error')

    return render_template('offerta/respond_offerta.html', offerta=offerta, case=immobile)


@bp.route('/offerta/<int:offerta_id>/delete', methods=('POST',))
def delete_offerta(offerta_id):
    """Elimina un'offerta."""
    if g.user is None:
        return redirect(url_for('auth.registerElogin'))
    
    offerta = offerte_repository.get_offerta_by_id(offerta_id)
    if offerta is None:
        abort(404)
    
    # Verifica che l'utente sia il proprietario dell'immobile
    immobile = immobile_repository.get_immobile_by_id(offerta['immobile_id'])
    if immobile['author_id'] != g.user['id']:
        abort(403)
    
    success = offerte_repository.delete_offerta(offerta_id)
    if success:
        flash('Offerta eliminata.', 'success')
    else:
        flash('Errore nell\'eliminazione.', 'error')
    
    return redirect(url_for('main.offerte'))


# --- ROUTE PER LE REVIEWS (COMMENTI ANONIMI E RISPOSTE) ---

@bp.route('/<int:immobile_id>/reviews', methods=('GET', 'POST'))
def view_case_reviews(immobile_id):
    """Mostra tutti i commenti su un immobile e permette di aggiungerne uno."""
    immobile = immobile_repository.get_immobile_by_id(immobile_id)
    if immobile is None:
        abort(404)
    
    reviews = review_repository.get_reviews_for_immobile(immobile_id)
    avg_rating = review_repository.get_average_rating_for_immobile(immobile_id)
    
    # POST: Aggiungere un nuovo commento anonimo
    if request.method == 'POST':
        reviewer_name = request.form.get('reviewer_name', '').strip()
        reviewer_email = request.form.get('reviewer_email', '').strip()
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        
        error = None
        if not reviewer_name:
            error = 'Il nome è obbligatorio.'
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            error = 'Valutazione non valida (1-5 stelle).'
        
        if error:
            flash(error, 'error')
        else:
            new_id = review_repository.create_review(immobile_id, reviewer_name, rating, comment, reviewer_email)
            if new_id:
                flash('Commento aggiunto con successo!', 'success')
                return redirect(url_for('main.view_case_reviews', immobile_id=immobile_id))
            else:
                flash('Errore nell\'aggiunta del commento.', 'error')
    
    return render_template('reviews/view_case_reviews.html', case=immobile, reviews=reviews, avg_rating=avg_rating)


@bp.route('/review/<int:review_id>/respond', methods=('POST',))
def respond_to_review(review_id):
    """Permette al proprietario di rispondere a un commento."""
    if g.user is None:
        abort(401)
    
    review = review_repository.get_review_by_id(review_id)
    if review is None:
        abort(404)
    
    # Verifica che sia il proprietario dell'immobile
    immobile = immobile_repository.get_immobile_by_id(review['immobile_id'])
    if immobile['author_id'] != g.user['id']:
        abort(403)
    
    response_text = request.form.get('owner_response', '').strip()
    if not response_text:
        flash('La risposta non può essere vuota.', 'error')
    else:
        success = review_repository.add_owner_response(review_id, response_text)
        if success:
            flash('Risposta aggiunta con successo!', 'success')
        else:
            flash('Errore nell\'aggiunta della risposta.', 'error')
    
    return redirect(url_for('main.view_case_reviews', immobile_id=review['immobile_id']))


@bp.route('/review/<int:review_id>/delete', methods=('POST',))
def delete_review(review_id):
    """Delete disabled: application policy forbids deleting reviews.

    Any attempt to call this route will be rejected with 403 Forbidden.
    """
    abort(403)


@bp.route('/my-reviews-received')
def my_reviews_received():
    """Mostra tutte le reviews ricevute dal proprietario (sui suoi immobili)."""
    if g.user is None or g.user.get('tipo_utente') != 'proprietario':
        flash('Solo i proprietari possono vedere i commenti ricevuti.', 'error')
        return redirect(url_for('main.index'))
    
    owner_reviews = review_repository.get_reviews_for_owner(g.user['id'])
    
    # Prepara dizionario immobili_by_id per il template
    immobili_by_id = {}
    for review in owner_reviews:
        immobile_id = review['immobile_id']
        if immobile_id not in immobili_by_id:
            immobile = immobile_repository.get_immobile_by_id(immobile_id)
            immobili_by_id[immobile_id] = immobile
    
    # Calcola statistiche
    total_reviews = len(owner_reviews)
    pending_responses = sum(1 for r in owner_reviews if not r['owner_response'])
    
    # Media complessiva
    overall_avg = None
    if total_reviews > 0:
        total_rating = sum(r['rating'] for r in owner_reviews)
        overall_avg = total_rating / total_reviews
    
    # Support server-side opening of a response form: ?open_review=<id>
    open_review = request.args.get('open_review')
    try:
        open_review_id = int(open_review) if open_review is not None else None
    except Exception:
        open_review_id = None

    return render_template('reviews/my_reviews_received.html', 
                           owner_reviews=owner_reviews,
                           immobili_by_id=immobili_by_id,
                           total_reviews=total_reviews,
                           pending_responses=pending_responses,
                           overall_avg=overall_avg,
                           open_review_id=open_review_id)
