from flask_mail import Mail, Message
from datetime import datetime
from app.db import get_db

mail = Mail()

def init_mail(app):
    """Inizializza Flask-Mail con la configurazione dell'app."""
    mail.init_app(app)

def send_welcome_email(coinquilino_nome, coinquilino_email, importo, giorno, case_via, case_civico, sender_name=None, sender_email=None):
    """Invia email di benvenuto con tutte le informazioni di pagamento.
    Se `sender_name` e `sender_email` sono forniti, impostiamo il mittente come (name, email).
    """
    try:
        kwargs = {}
        if sender_name and sender_email:
            kwargs['sender'] = (sender_name, sender_email)

        msg = Message(
            subject=f'👋 Benvenuto nel gestionale casa - {case_via}',
            recipients=[coinquilino_email],
            html=f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f9f9f9;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <h1 style="color: #333;">Benvenuto, {coinquilino_nome}! 👋</h1>
                        <p style="color: #666; font-size: 16px;">Sei stato aggiunto al gestionale della casa. Ecco le tue informazioni di pagamento:</p>
                        
                        <div style="background-color: #e8f4f8; padding: 25px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #0099cc;">
                            <h2 style="color: #0099cc; margin-top: 0;">📋 Dettagli Pagamento</h2>
                            <p style="margin: 10px 0;"><strong>Casa:</strong> {case_via}, {case_civico}</p>
                            <p style="margin: 10px 0;"><strong>Importo Mensile:</strong> €{importo:.2f}</p>
                            <p style="margin: 10px 0;"><strong>Giorno Pagamento:</strong> {giorno}° di ogni mese</p>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;">
                            <h3 style="color: #ff9800; margin-top: 0;">⏰ Ricordati</h3>
                            <p style="color: #666;">Il pagamento è dovuto il <strong>{giorno}° di ogni mese</strong>. Riceverai un reminder automatico quando arriverà la data!</p>
                        </div>
                        
                        <hr style="border: none; border-top: 2px solid #eee; margin: 30px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">Messaggio automatico dal gestionale casa</p>
                    </div>
                </body>
            </html>
            """,
            **kwargs
        )
        mail.send(msg)
        print(f"✅ Email di benvenuto inviata a {coinquilino_nome}")
        return True
    except Exception as e:
        print(f"❌ Errore nell'invio email di benvenuto: {e}")
        return False

def send_payment_reminder(coinquilino_email, coinquilino_nome, importo, case_via):
    """Invia un reminder di pagamento via email."""
    try:
        msg = Message(
            subject=f'💰 Reminder: Pagamento dovuto - {case_via}',
            recipients=[coinquilino_email],
            html=f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Ciao {coinquilino_nome}! 👋</h2>
                    <p>È arrivato il giorno del tuo pagamento!</p>
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3>Importo dovuto: €{importo}</h3>
                        <p><strong>Casa:</strong> {case_via}</p>
                        <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
                    </div>
                    <p>Ricordati di effettuare il pagamento! 💳</p>
                    <hr>
                    <p><small>Messaggio automatico dal gestionale casa</small></p>
                </body>
            </html>
            """
        )
        mail.send(msg)
        
        # Salva il timestamp dell'ultimo invio
        update_last_sent(coinquilino_id=None, email=coinquilino_email)
        return True
    except Exception as e:
        print(f"Errore nell'invio email: {e}")
        return False

def update_last_sent(coinquilino_id=None, email=None):
    """Aggiorna il timestamp dell'ultimo reminder inviato."""
    db = get_db()
    try:
        if coinquilino_id:
            db.execute(
                'UPDATE coinquilini SET last_sent = CURRENT_TIMESTAMP WHERE id = ?',
                (coinquilino_id,)
            )
        elif email:
            db.execute(
                'UPDATE coinquilini SET last_sent = CURRENT_TIMESTAMP WHERE email = ?',
                (email,)
            )
        db.commit()
    except Exception as e:
        print(f"Errore nell'aggiornamento: {e}")

def check_and_send_reminders():
    """Controlla tutti i coinquilini e invia reminder se è il giorno del pagamento."""
    db = get_db()
    from datetime import date
    
    today = date.today().day  # Giorno del mese (1-31)
    
    try:
        # Cerca tutti i coinquilini dove giorno_pagamento == oggi
        coinquilini = db.execute(
            '''SELECT c.id, c.nome, c.email, c.importo, casa.via 
               FROM coinquilini c
               JOIN "case" casa ON c.case_id = casa.id
               WHERE c.giorno = ?''',
            (today,)
        ).fetchall()
        
        for coinquilino in coinquilini:
            # Controlla se non abbiamo già inviato un reminder questo mese
            last_sent = db.execute(
                'SELECT last_sent FROM coinquilini WHERE id = ?',
                (coinquilino['id'],)
            ).fetchone()
            
            # Se last_sent è null o non è di questo mese, invia
            if not last_sent['last_sent'] or not is_same_month(last_sent['last_sent']):
                send_payment_reminder(
                    coinquilino_email=coinquilino['email'],
                    coinquilino_nome=coinquilino['nome'],
                    importo=coinquilino['importo'],
                    case_via=coinquilino['via']
                )
                print(f"✅ Email inviata a {coinquilino['nome']}")
        
        return len(coinquilini)
    except Exception as e:
        print(f"Errore nel controllo reminder: {e}")
        return 0


def send_reply_notification(to_email, proprietario_nome, casa_via, risposta_text):
        """Invia una email all'offerente quando il proprietario risponde all'offerta.
        Imposta il mittente con il nome del proprietario se possibile.
        """
        from flask import current_app
        try:
                subject = f"Risposta alla tua offerta per {casa_via}"
                html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2>Ciao!</h2>
                        <p>Hai ricevuto una risposta dal proprietario <strong>{proprietario_nome}</strong> per la casa <strong>{casa_via}</strong>.</p>
                        <div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:15px 0;">
                            <strong>Risposta:</strong>
                            <p>{risposta_text}</p>
                        </div>
                        <p>Accedi al gestionale per vedere tutte le notifiche.</p>
                        <hr>
                        <p style="font-size:12px;color:#888;">Messaggio automatico dal gestionale casa</p>
                    </body>
                </html>
                """
                sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
                try:
                    msg = Message(subject=subject, recipients=[to_email], html=html, sender=(proprietario_nome, sender_email))
                except Exception:
                    msg = Message(subject=subject, recipients=[to_email], html=html)
                mail.send(msg)
                return True
        except Exception as e:
                print(f"Errore invio reply notification: {e}")
                return False

def is_same_month(last_sent_str):
    """Controlla se last_sent è dello stesso mese di oggi."""
    from datetime import datetime
    if not last_sent_str:
        return False
    
    try:
        last_sent = datetime.fromisoformat(last_sent_str)
        today = datetime.now()
        return last_sent.year == today.year and last_sent.month == today.month
    except:
        return False
