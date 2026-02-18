# run_server.py
# -----------------------------------------------------------------------------
# Point d'entrée pour l'exécutable Windows (PyInstaller).
# Définit le répertoire de travail au dossier de l'exe pour que .env et app/db
# soient trouvés, puis lance uvicorn. En cas d'erreur, affiche le message et garde
# la fenêtre ouverte (double-clic sur l'exe).
# -----------------------------------------------------------------------------

import os
import sys


def _set_working_dir():
    """Place le répertoire de travail au dossier contenant l'exécutable."""
    if getattr(sys, "frozen", False):
        # Exécution en mode PyInstaller (exe)
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)
    return base


# Clé par défaut si aucun .env (exe Windows) — défini avant get_settings()
_DEFAULT_SECRET_KEY = "gesco-dev-default-change-me-in-production-32c"


def _main():
    base = _set_working_dir()
    # Si exe et pas de SECRET_KEY dans l'environnement, utiliser la valeur par défaut
    # (évite l'erreur "Field required" avec un exe construit avant l'ajout du default dans config)
    if getattr(sys, "frozen", False) and not os.environ.get("SECRET_KEY"):
        os.environ["SECRET_KEY"] = _DEFAULT_SECRET_KEY
    # Créer app/db pour SQLite si besoin (exécutable portable)
    os.makedirs(os.path.join(base, "app", "db"), exist_ok=True)
    import uvicorn
    from app.config import get_settings
    s = get_settings()
    if getattr(sys, "frozen", False) and s.SECRET_KEY == _DEFAULT_SECRET_KEY:
        print("Attention : SECRET_KEY par défaut. Pour la production, créez un fichier .env avec SECRET_KEY=...", file=sys.stderr)
    uvicorn.run(
        "app.main:app",
        host=s.HOST,
        port=s.PORT,
        log_level="info" if not s.DEBUG else "debug",
    )


if __name__ == "__main__":
    try:
        _main()
    except Exception as exc:
        import traceback
        print("=" * 60, file=sys.stderr)
        print("ERREUR au démarrage de Gesco", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        traceback.print_exc()
        print("=" * 60, file=sys.stderr)
        if getattr(sys, "frozen", False):
            input("Appuyez sur Entrée pour fermer...")
        raise
