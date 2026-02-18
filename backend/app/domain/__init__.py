# app/domain
# -----------------------------------------------------------------------------
# Couche Domain (Clean Architecture) : entités métier et exceptions domaine.
# Aucune dépendance vers l'infrastructure (DB, HTTP) ou la présentation.
# Les exceptions domaine (DomainError, DomainNotFoundError, etc.) sont définies
# dans app.domain.exceptions ; le projet utilise actuellement app.core.exceptions
# pour les réponses HTTP. Pour un mapping domaine → HTTP, importer depuis
# app.domain.exceptions.
# -----------------------------------------------------------------------------

