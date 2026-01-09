DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS offerte;
DROP TABLE IF EXISTS coinquilini;
DROP TABLE IF EXISTS immobili;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  first_name TEXT NOT NULL DEFAULT '',
  last_name TEXT NOT NULL DEFAULT '',
  profile_photo TEXT,
  tipo_utente TEXT NOT NULL DEFAULT 'proprietario',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE immobili (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  via TEXT NOT NULL,
  civico TEXT NOT NULL,
  tipo_annuncio TEXT NOT NULL DEFAULT 'affitto',
  photo TEXT,
  price_rent REAL,
  price_sale REAL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE coinquilini (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  immobile_id INTEGER NOT NULL,
  nome TEXT NOT NULL,
  cognome TEXT NOT NULL,
  email TEXT NOT NULL,
  importo REAL NOT NULL,
  giorno INTEGER NOT NULL,
  numero_persone INTEGER,
  eta INTEGER,
  last_sent TIMESTAMP,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (immobile_id) REFERENCES immobili (id) ON DELETE CASCADE
);

CREATE TABLE offerte (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  immobile_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  nome TEXT NOT NULL,
  cognome TEXT NOT NULL,
  email TEXT NOT NULL,
  numero_telefono TEXT,
  messaggio TEXT NOT NULL,
  read INTEGER DEFAULT 0,
  risposta TEXT,
  risposta_created TIMESTAMP,
  risposta_letta INTEGER DEFAULT 0,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (immobile_id) REFERENCES immobili (id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  immobile_id INTEGER NOT NULL,
  reviewer_name TEXT NOT NULL,
  reviewer_email TEXT,
  rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
  comment TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated TIMESTAMP,
  owner_response TEXT,
  owner_response_created TIMESTAMP,
  FOREIGN KEY (immobile_id) REFERENCES immobili (id) ON DELETE CASCADE
);
