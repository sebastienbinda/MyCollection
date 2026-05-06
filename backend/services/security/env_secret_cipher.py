#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-06
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : classe utilitaire de chiffrement et dechiffrement des secrets .env.

from cryptography.fernet import Fernet, InvalidToken


class EnvSecretCipher:
    """Chiffre et dechiffre les secrets stockes dans les variables d'environnement."""

    TOKEN_PREFIX = "fernet:"

    def __init__(self, encryption_key: str):
        """Initialise le chiffreur de secrets d'environnement.

        Args:
            encryption_key (str): Cle Fernet encodee en base64 URL-safe.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.encryption_key = encryption_key.strip()
        self._fernet = Fernet(self.encryption_key.encode("ascii"))

    @classmethod
    def generate_key(cls) -> str:
        """Genere une cle de chiffrement Fernet.

        Args:
            Aucun.

        Returns:
            str: Cle Fernet encodee en base64 URL-safe.
        """

        return Fernet.generate_key().decode("ascii")

    def encrypt(self, plain_value: str) -> str:
        """Chiffre une valeur en clair pour stockage dans un fichier .env.

        Args:
            plain_value (str): Valeur secrete en clair.

        Returns:
            str: Jeton chiffre prefixe par `fernet:`.
        """

        token = self._fernet.encrypt(plain_value.encode("utf-8")).decode("ascii")
        return f"{self.TOKEN_PREFIX}{token}"

    def decrypt(self, encrypted_value: str) -> str:
        """Dechiffre une valeur issue du fichier .env.

        Args:
            encrypted_value (str): Valeur chiffree, avec ou sans prefixe `fernet:`.

        Returns:
            str: Valeur secrete en clair.
        """

        token = self._strip_prefix(encrypted_value)
        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Secret d'environnement chiffre invalide.") from exc

    def _strip_prefix(self, encrypted_value: str) -> str:
        """Retire le prefixe applicatif d'une valeur chiffree.

        Args:
            encrypted_value (str): Valeur chiffree brute ou prefixee.

        Returns:
            str: Jeton Fernet sans prefixe applicatif.
        """

        value = encrypted_value.strip()
        if value.startswith(self.TOKEN_PREFIX):
            return value[len(self.TOKEN_PREFIX) :]
        return value
