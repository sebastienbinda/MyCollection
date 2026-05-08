#!/usr/bin/env python3
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
# Description : utilitaire objet de generation des secrets d'authentification et Postgres chiffres.

import argparse
import secrets
import string
import sys
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parents[1]
SECURITY_DIR = PROJECT_DIR / "backend" / "services" / "security"
sys.path.insert(0, str(SECURITY_DIR))

from env_secret_cipher import EnvSecretCipher  # noqa: E402


class AuthEnvGenerator:
    """Genere les secrets applicatifs et Postgres pour `.env`."""

    DEFAULT_PASSWORD_LENGTH = 24
    DEFAULT_POSTGRES_PASSWORD_LENGTH = 32
    DEFAULT_SECRET_KEY_BYTES = 48

    def __init__(
        self,
        password_length: int,
        secret_key_bytes: int,
        postgres_password_length: int = DEFAULT_POSTGRES_PASSWORD_LENGTH,
    ):
        """Initialise le generateur de secrets d'authentification.

        Args:
            password_length (int): Taille du mot de passe genere.
            secret_key_bytes (int): Nombre d'octets aleatoires pour la cle HMAC.
            postgres_password_length (int): Taille du mot de passe Postgres genere.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.password_length = password_length
        self.secret_key_bytes = secret_key_bytes
        self.postgres_password_length = postgres_password_length

    def generate(self) -> dict[str, str]:
        """Genere les secrets en clair et leurs versions chiffrees.

        Args:
            Aucun.

        Returns:
            dict[str, str]: Variables d'environnement pretes a copier dans `.env`.
        """

        encryption_key = EnvSecretCipher.generate_key()
        cipher = EnvSecretCipher(encryption_key)
        password = self._generate_password()
        postgres_password = self._generate_password(self.postgres_password_length)
        secret_key = secrets.token_urlsafe(self.secret_key_bytes)

        return {
            "AUTH_ENV_ENCRYPTION_KEY": encryption_key,
            "AUTH_PASSWORD_ENCRYPTED": cipher.encrypt(password),
            "AUTH_SECRET_KEY_ENCRYPTED": cipher.encrypt(secret_key),
            "POSTGRES_PASSWORD": postgres_password,
            "POSTGRES_PASSWORD_ENCRYPTED": cipher.encrypt(postgres_password),
            "GENERATED_AUTH_PASSWORD": password,
            "GENERATED_AUTH_SECRET_KEY": secret_key,
            "GENERATED_POSTGRES_PASSWORD": postgres_password,
        }

    def _generate_password(self, length: Optional[int] = None) -> str:
        """Genere un mot de passe compatible avec un fichier .env.

        Args:
            length (Optional[int]): Taille du mot de passe a generer.

        Returns:
            str: Mot de passe aleatoire sans espace ni guillemets.
        """

        alphabet = string.ascii_letters + string.digits + "-_"
        password_length = length or self.password_length
        return "".join(secrets.choice(alphabet) for _ in range(password_length))


class AuthEnvCli:
    """Expose le generateur de secrets d'authentification en ligne de commande."""

    def run(self, argv: Optional[list[str]] = None) -> int:
        """Execute la commande de generation.

        Args:
            argv (Optional[list[str]]): Arguments CLI optionnels sans le nom du programme.

        Returns:
            int: Code de sortie de la commande.
        """

        args = self._build_parser().parse_args(argv)
        values = AuthEnvGenerator(
            args.password_length,
            args.secret_key_bytes,
            args.postgres_password_length,
        ).generate()
        self._print_values(values)
        return 0

    def _build_parser(self) -> argparse.ArgumentParser:
        """Construit le parseur d'arguments du script.

        Args:
            Aucun.

        Returns:
            argparse.ArgumentParser: Parseur configure pour la commande.
        """

        parser = argparse.ArgumentParser(
            description="Genere les mots de passe et cles chiffres pour .env."
        )
        parser.add_argument(
            "--password-length",
            type=int,
            default=AuthEnvGenerator.DEFAULT_PASSWORD_LENGTH,
            help="Taille du mot de passe genere.",
        )
        parser.add_argument(
            "--secret-key-bytes",
            type=int,
            default=AuthEnvGenerator.DEFAULT_SECRET_KEY_BYTES,
            help="Nombre d'octets aleatoires utilises pour AUTH_SECRET_KEY.",
        )
        parser.add_argument(
            "--postgres-password-length",
            type=int,
            default=AuthEnvGenerator.DEFAULT_POSTGRES_PASSWORD_LENGTH,
            help="Taille du mot de passe Postgres genere.",
        )
        return parser

    def _print_values(self, values: dict[str, str]) -> None:
        """Affiche les variables generees.

        Args:
            values (dict[str, str]): Variables generees par `AuthEnvGenerator`.

        Returns:
            None: Les valeurs sont ecrites sur la sortie standard.
        """

        for key, value in values.items():
            print(f"{key}={value}")


if __name__ == "__main__":
    raise SystemExit(AuthEnvCli().run())
