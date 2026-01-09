# Gestionale Case

Applicazione web minima realizzata con Python + Flask per gestire immobili, offerte e commenti anonimi.

Questo README contiene le istruzioni essenziali per avviare e usare il progetto.

Se usi questa copia per una valutazione, qui trovi solo ciò che serve per farla partire e dimostrare le funzionalità.

---

## Panoramica

- Tecnologia: Python 3.10+, Flask, SQLite, Jinja2, Bootstrap 5
- Scopo: gestione CRUD di immobili, gestione coinquilini, invio/ricezione offerte, commenti anonimi con valutazione e risposta del proprietario
- Upload: foto profilo e foto immobile salvate in `instance/uploads` e servite tramite la route `/uploads/<filename>`

---

<!-- README aggiornato: versione più chiara e ordinata -->
# Gestionale Case — App di esempio (2025)

Breve applicazione web realizzata con Python e Flask per la gestione di immobili, offerte e recensioni.

- Linguaggi e librerie: Python 3.10+, Flask, SQLite, Jinja2, Bootstrap 5
- Scopo: dimostrare funzionalità CRUD per immobili, gestione coinquilini, gestione offerte e sistema di recensioni anonime.

---

## Caratteristiche principali

- Creazione/lettura/aggiornamento/cancellazione di immobili
- Upload e visualizzazione di immagini per immobili e profili (cartella `instance/uploads`)
- Invio e ricezione di offerte
- Recensioni anonime con valutazione 1–5 e possibilità di risposta da parte del proprietario
- Interfaccia responsive costruita con Bootstrap 5

---

## Installazione veloce (locale)

1. Crea e attiva un ambiente virtuale

Windows (PowerShell):
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Installa le dipendenze

```bash
py -m pip install -r requirements.txt
```

3. Crea il database di esempio

```bash
py setup_db.py
```

4. Avvia l'app

```bash
py run.py
# Apri nel browser: http://127.0.0.1:5000
```

Credenziali di prova incluse nel seed:

- Username: bob
- Password: password123

---

## Struttura del progetto

- `run.py` — entrypoint
- `app/` — codice applicazione (blueprints, templates, repositories)
- `app/templates/` — template Jinja2
- `app/repositories/` — logica accesso dati (immobili, utenti, offerte, recensioni)
- `app/schema.sql`, `app/seed.json` — schema e dati di esempio
- `instance/uploads/` — immagini caricate a runtime

---

## Come provare le funzionalità (rapido walkthrough)

1. Esegui login con le credenziali di test
2. Crea un immobile e carica una foto
3. Visualizza la scheda immobile e lascia una recensione anonima
4. Effettua il login come proprietario e rispondi alle recensioni dalla dashboard

---

## Note tecniche

- Gli upload sono serviti da una route che usa `send_from_directory` (vedi `app/__init__.py`).
- Il progetto favorisce logica lato server per rendere i flussi più chiari in fase di presentazione/dimostrazione.

---

## Contatti e autore

Progetto sviluppato da Cristian — per richieste o modifiche, apri una issue o modifica direttamente il repository.

---

Ultimo aggiornamento: 2026-01-07

