# app/core/logging_config.py
# -----------------------------------------------------------------------------
# Configuration du logging à partir des paramètres (LOG_LEVEL, LOG_FORMAT, LOG_FILE).
# -----------------------------------------------------------------------------

import logging
import sys


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: str | None = None,
) -> None:
    """
    Configure le logger racine de l'application.
    :param level: DEBUG | INFO | WARNING | ERROR
    :param format_type: json | text
    :param log_file: Chemin du fichier de log (None = console uniquement)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    if format_type == "json":
        # Format structuré pour ingestion (ex: ELK)
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    root = logging.getLogger()
    root.setLevel(log_level)
    # Retirer les handlers existants pour éviter doublons
    for h in root.handlers[:]:
        root.removeHandler(h)
    # Console
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)
    # Fichier optionnel
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except OSError:
            root.warning("Impossible d'ouvrir le fichier de log %s", log_file)


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger pour le module donné."""
    return logging.getLogger(name)

