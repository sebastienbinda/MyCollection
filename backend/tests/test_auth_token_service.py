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
# Description : tests unitaires du service d'authentification par token Bearer.

import unittest

from services.auth import AuthTokenService


class AuthTokenServiceTest(unittest.TestCase):
    def setUp(self):
        """Prepare un service d'authentification deterministe.

        Args:
            Aucun.

        Returns:
            None: Le service est stocke pour chaque test.
        """

        self.service = AuthTokenService(
            username="admin",
            password="secret",
            secret_key="unit-test-secret",
            token_ttl_seconds=3600,
        )

    def test_issue_token_returns_oauth2_payload(self):
        """Verifie le format de la reponse OAuth2.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le token genere.
        """

        token_response = self.service.issue_token("admin", "secret")

        self.assertEqual("Bearer", token_response["token_type"])
        self.assertEqual(3600, token_response["expires_in"])
        self.assertIn(".", token_response["access_token"])

    def test_validate_access_token_returns_payload(self):
        """Verifie qu'un token signe valide retourne son payload.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le sujet du token.
        """

        token = self.service.create_access_token("admin")

        payload = self.service.validate_access_token(token)

        self.assertEqual("admin", payload["sub"])

    def test_issue_token_rejects_invalid_credentials(self):
        """Verifie le refus d'identifiants invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur levee.
        """

        with self.assertRaises(ValueError):
            self.service.issue_token("admin", "bad-password")

    def test_validate_access_token_rejects_invalid_signature(self):
        """Verifie le refus d'un token modifie.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de signature.
        """

        token = self.service.create_access_token("admin")
        payload_segment, _ = token.split(".", 1)

        with self.assertRaises(ValueError):
            self.service.validate_access_token(f"{payload_segment}.bad-signature")

    def test_validate_access_token_rejects_expired_token(self):
        """Verifie le refus d'un token expire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur d'expiration.
        """

        expired_service = AuthTokenService(
            username="admin",
            password="secret",
            secret_key="unit-test-secret",
            token_ttl_seconds=-1,
        )
        token = expired_service.create_access_token("admin")

        with self.assertRaises(ValueError):
            expired_service.validate_access_token(token)


if __name__ == "__main__":
    unittest.main()
