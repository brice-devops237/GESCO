# app/modules/auth
# -----------------------------------------------------------------------------
# Module Authentification : connexion (login/email + mot de passe), JWT, profil courant.
#
# Extension du monde réel, adaptée à TOUTES les structures (taille) et TOUS les
# secteurs (commerce, industrie, services, etc.) :
#
# - Taille : PME (un PDV, peu d'utilisateurs) ou grand groupe (multi-PDV, rôles
#   multiples) : l'auth ne suppose ni taille ni secteur ; le contexte (entreprise,
#   rôle, permissions) est géré par le module parametrage (get_current_user,
#   permissions par rôle). /me expose entreprise_id et role_id pour adapter l'UI.
# - Secteur : aucun métier spécifique dans l'auth ; identifiant (login ou email),
#   mot de passe, JWT et contexte entreprise suffisent pour tout secteur.
# - Identifiant : login ou email (normalisé, strip), une seule entrée.
# - Contexte entreprise : un utilisateur = une entreprise (token et /me) ; mono-
#   société natif ; multi-société possible en extension (switch de contexte).
# - Autorisation : rôles et permissions sont dans parametrage (Role, Permission,
#   PermissionRole) ; les routes protégées utilisent get_current_user puis
#   vérifient les permissions selon les besoins métier.
# - Sécurité : message unique « Identifiants incorrects », bcrypt (BCRYPT_ROUNDS),
#   JWT expires_in (RFC 6749), durée token configurable (ACCESS_TOKEN_EXPIRE_MINUTES).
# - GET /auth/me : profil minimal + entreprise_id + role_id pour « connecté en tant que ».
# -----------------------------------------------------------------------------

