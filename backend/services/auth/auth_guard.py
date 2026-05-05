#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-05
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : garde d'authentification pour proteger les routes Flask mutantes.

from functools import wraps
from typing import Callable

from flask import jsonify, request

from .auth_token_service import AuthTokenService


class AuthGuard:
    """Applique la validation Bearer OAuth2 aux endpoints Flask proteges."""

    def __init__(self, token_service: AuthTokenService):
        """Initialise le garde d'authentification.

        Args:
            token_service (AuthTokenService): Service utilise pour valider les tokens.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.token_service = token_service

    def require_token(self, route_handler: Callable) -> Callable:
        """Retourne un decorateur qui exige un token Bearer valide.

        Args:
            route_handler (Callable): Fonction Flask a proteger.

        Returns:
            Callable: Fonction enveloppee avec verification d'authentification.
        """

        @wraps(route_handler)
        def wrapped_route(*args, **kwargs):
            """Valide le header `Authorization` avant d'appeler la route.

            Args:
                *args (tuple): Arguments positionnels transmis par Flask.
                **kwargs (dict): Arguments nommes transmis par Flask.

            Returns:
                Any: Reponse de la route originale ou erreur JSON 401.
            """

            token = self._extract_bearer_token()
            if not token:
                return self._unauthorized_response("Token Bearer manquant.")

            try:
                self.token_service.validate_access_token(token)
            except ValueError as exc:
                return self._unauthorized_response(str(exc))
            return route_handler(*args, **kwargs)

        wrapped_route.requires_auth = True
        return wrapped_route

    def _extract_bearer_token(self) -> str:
        """Extrait le token Bearer depuis l'en-tete HTTP.

        Args:
            Aucun.

        Returns:
            str: Token extrait, ou chaine vide si absent.
        """

        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return ""
        return token.strip()

    def _unauthorized_response(self, message: str):
        """Construit une reponse HTTP 401 compatible OAuth2 Bearer.

        Args:
            message (str): Message d'erreur a retourner au client.

        Returns:
            tuple[flask.Response, int, dict[str, str]]: Reponse JSON 401 avec challenge Bearer.
        """

        return (
            jsonify({"error": message}),
            401,
            {"WWW-Authenticate": 'Bearer realm="CloudCollectionApp"'},
        )
