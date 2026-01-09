from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import os
from werkzeug.utils import secure_filename
# werkzeug.security ci offre strumenti professionali per la crittografia
from werkzeug.security import check_password_hash, generate_password_hash
from app.repositories import user_repository
from app.file_utils import allowed_file, generate_saved_filename

# url_prefix='/auth' significa che tutte le route qui inizieranno con /auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    """
    Questa funzione viene eseguita AUTOMATICAMENTE prima di ogni richiesta.
    Serve a caricare l'utente dal DB e renderlo disponibile in tutto il sito.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Carichiamo l'utente e lo mettiamo in g.user
        # Convertiamo a dict per rendere disponibili i metodi come .get() nei template
        user = user_repository.get_user_by_id(user_id)
        g.user = dict(user) if user is not None else None

@bp.route('/auth.loginEregister', methods=('GET', 'POST'))
def loginEregister():
    # CASO 2: POST (L'utente ha inviato i dati)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        tipo_utente = request.form.get('tipo_utente', 'proprietario')
        
        error = None
        user = user_repository.get_user_by_username(username)
        if user is None:
            if not username:
                error = 'Username obbligatorio.'
            elif not email:
                error = 'Email obbligatoria.'
            elif not password:
                error = 'Password obbligatoria.'

            if error is None:
                # Hashiamo la password (MAI salvarla in chiaro!)
                hashed_pwd = generate_password_hash(password)
                # Nome e cognome
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()

                # Foto profilo NON viene caricata qui, solo in account modification
                profile_filename = None

                # Chiamiamo il Repository includendo nome/cognome/foto
                success = user_repository.create_user(username, email, hashed_pwd, first_name, last_name, profile_filename, tipo_utente)

                if success:
                    flash(f'Utente {username} registrato con successo come {tipo_utente}! Effettua il login.', 'success')
                    return redirect(url_for('auth.loginEregister'))
                else:
                    error = f"L'utente {username} è già registrato."
        #================================================
        
        else:
            if user is None:
                error = 'Username non corretto.'
            # 2. Verifichiamo la password
            elif not check_password_hash(user['password'], password):
                error = 'Password non corretta.'

            if error is None:
                # 3. GESTIONE SESSIONE (Mettiamo il "braccialetto")
                # Puliamo eventuali vecchie sessioni
                session.clear()
                # Salviamo l'ID dell'utente nel cookie di sessione
                session['user_id'] = user['id']
                
                # Ora il browser ricorderà chi siamo!
                flash(f'Benvenuto/a {username}!', 'success')
                return redirect(url_for('main.index'))

        flash(error, 'error')

        

    # CASO 1: GET (Mostriamo il form)
    return render_template('auth/loginEregister.html')

@bp.route('/logout')
def logout():
    # Per uscire, "tagliamo il braccialetto"
    session.clear()
    return redirect(url_for('main.index'))

# La route `/login` era una duplicazione di `loginEregister()` che gestisce
# sia registrazione che login in un unico endpoint. Rimossa per evitare confusione.


@bp.route('/account', methods=('GET', 'POST'))
def account():
    # Modifica dati account: nome, cognome, email, username, password e foto profilo
    if g.user is None:
        return redirect(url_for('auth.loginEregister'))

    if request.method == 'POST':
        username = request.form.get('username', g.user.get('username'))
        email = request.form.get('email', g.user.get('email'))
        first_name = request.form.get('first_name', g.user.get('first_name', ''))
        last_name = request.form.get('last_name', g.user.get('last_name', ''))
        password = request.form.get('password')

        profile_filename = g.user.get('profile_photo')
        profile_file = request.files.get('profile_photo')
        if profile_file and profile_file.filename:
            if allowed_file(profile_file.filename):
                filename = generate_saved_filename(profile_file.filename, prefix=username)
                profile_filename = filename
                upload_folder = current_app.config.get('UPLOAD_FOLDER')
                if upload_folder:
                    os.makedirs(upload_folder, exist_ok=True)
                    profile_file.save(os.path.join(upload_folder, profile_filename))
            else:
                flash('Formato immagine non consentito. Usa png/jpg/jpeg/gif', 'error')
                return render_template('auth/account.html', user=g.user)

        password_hash = generate_password_hash(password) if password else None
        success = user_repository.update_user(
            g.user['id'], username=username, email=email, first_name=first_name, last_name=last_name, profile_photo=profile_filename, password_hash=password_hash
        )
        if success:
            # Ricarichiamo l'utente per aggiornare la sessione
            user = user_repository.get_user_by_id(g.user['id'])
            g.user = dict(user) if user is not None else None
            flash('Account aggiornato con successo.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Errore nell\'aggiornamento dell\'account.', 'error')

    return render_template('auth/account.html', user=g.user)
