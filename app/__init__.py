import os
from flask import Flask, abort
from flask_mail import Mail

def create_app():
    # 1. Creiamo l'istanza di Flask
    # instance_relative_config=True dice a Flask: 
    # "Cerca la cartella 'instance' fuori da 'app', non dentro."
    app = Flask(__name__, instance_relative_config=True)

    # 2. Configurazione di base
    # Qui impostiamo le variabili fondamentali.
    app.config.from_mapping(
        # SECRET_KEY serve a Flask per firmare i dati sicuri (es. sessioni).
        # 'dev' va bene per sviluppare, ma in produzione andrà cambiata.
        SECRET_KEY='dev',
        # Diciamo a Flask dove salvare il file del database SQLite
        DATABASE=os.path.join(app.instance_path, 'gestionale.sqlite'),
        # Cartella per upload foto profilo
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        # Limite upload file a 5 MB
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        # Configurazione Email (Gmail o altro provider)
        MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', True),
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME', 'tua-email@gmail.com'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', 'tua-password'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@gestionale-casa.it'),
    )

    # --- AGGIUNGI QUESTO ---
    from . import db
    db.init_app(app)
    # Assicuriamoci che la cartella per gli upload esista
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        try:
            os.makedirs(upload_folder, exist_ok=True)
        except Exception:
            pass
    # -----------------------

    # --- INIZIALIZZA MAIL ---
    from . import notifications
    notifications.init_mail(app)
    # Gestione errore upload troppo grande
    from werkzeug.exceptions import RequestEntityTooLarge

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return 'File troppo grande', 413
    # -----------------------

    # --- REGISTRAZIONE BLUEPRINTS ---
    from . import main
    app.register_blueprint(main.bp)
    
    from . import auth
    app.register_blueprint(auth.bp)
    # --------------------------------

    # Route per servire i file caricati in runtime (profile e foto case)
    from flask import send_from_directory
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            abort(404)
        return send_from_directory(upload_folder, filename)


    return app