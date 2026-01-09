"""Utility per upload file: estensioni consentite e helper per i nomi di file."""
from werkzeug.utils import secure_filename

# Estensioni consentite per immagini
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Ritorna True se il filename ha un'estensione consentita."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_saved_filename(original_filename, prefix=None, max_length=100):
    """Genera un nome file sicuro e limitato a `max_length` caratteri.

    Se `prefix` è fornito, viene pre-penduto separato da underscore.
    """
    name = secure_filename(original_filename)
    if prefix:
        name = f"{prefix}_{name}"
    # Assicuriamoci che il nome non sia troppo lungo
    if len(name) > max_length:
        # manteniamo estensione
        parts = name.rsplit('.', 1)
        if len(parts) == 2:
            base, ext = parts
            base = base[: max_length - 1 - len(ext)]
            name = f"{base}.{ext}"
        else:
            name = name[:max_length]
    return name
