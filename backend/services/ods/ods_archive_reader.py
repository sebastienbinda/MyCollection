#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from zipfile import ZipFile

from .ods_cache import OdsCache


class OdsArchiveReader:
    def __init__(self, ods_path: str, cache: OdsCache):
        """Initialise le lecteur d'archive ODS.

        Args:
            ods_path (str): Chemin du fichier ODS.
            cache (OdsCache): Cache partage par le service.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path
        self.cache = cache

    def read_file(self, internal_path: str) -> bytes:
        """Lit un fichier interne de l'archive ODS avec cache.

        Args:
            internal_path (str): Chemin du fichier dans l'archive ODS.

        Returns:
            bytes: Contenu binaire du fichier interne.
        """

        return self.cache.remember(
            f"archive_file:{internal_path}",
            lambda: self._read_uncached_file(internal_path),
        )

    def _read_uncached_file(self, internal_path: str) -> bytes:
        """Lit un fichier interne de l'archive ODS sans cache.

        Args:
            internal_path (str): Chemin du fichier dans l'archive ODS.

        Returns:
            bytes: Contenu binaire lu depuis le disque.
        """

        with ZipFile(self.ods_path) as ods_archive:
            return ods_archive.read(internal_path)
