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
import os
from typing import Optional


class OdsPathResolver:
    def __init__(self, ods_path: Optional[str] = None):
        """Initialise le resolver de chemin ODS.

        Args:
            ods_path (Optional[str]): Chemin explicite optionnel vers le fichier ODS.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path

    def resolve(self) -> str:
        """Determine le chemin du fichier ODS a utiliser.

        Args:
            Aucun.

        Returns:
            str: Chemin absolu existant vers le fichier ODS.

        Raises:
            FileNotFoundError: Si aucun fichier ODS valide n'est trouve.
        """

        if self.ods_path:
            return self.ods_path

        env_path = os.getenv("JEUXVIDEO_ODS_PATH")
        candidate_paths = [
            env_path,
            "~/Documents/JeuxVideo-v2.ods",
            "~/Documents/Documents/JeuxVideo-v2.ods",
        ]
        resolved_path = next(
            (
                os.path.expanduser(path)
                for path in candidate_paths
                if path and os.path.exists(os.path.expanduser(path))
            ),
            None,
        )
        if not resolved_path:
            raise FileNotFoundError(
                "ODS file not found. Configure JEUXVIDEO_ODS_PATH to point to JeuxVideo-v2.ods."
            )
        return resolved_path
