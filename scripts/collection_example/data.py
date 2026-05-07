#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-07
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : donnees factices utilisees dans le fichier collection-example.ods.
from __future__ import annotations

from typing import Any


class CollectionExampleData:
    """Centralise les donnees publiques du fichier ODS exemple."""

    platform_columns = [
        "Nom du jeu",
        "Studio",
        "Date de sortie",
        "Date d'achat",
        "Lieu d'achat",
        "Note",
        "Prix d'achat",
        "Version",
    ]
    wishlist_columns = [
        "Nom du jeu",
        "Console",
        "Date de sortie",
        "Date d'achat",
        "Lieu d'achat",
        "Prix",
        "Studio",
    ]
    platform_images = {
        "Playstation": ("Pictures/example-playstation.png", (40, 90, 190), (180, 210, 255)),
        "Switch": ("Pictures/example-switch.png", (220, 65, 85), (255, 210, 215)),
        "PC": ("Pictures/example-pc.png", (70, 150, 120), (210, 245, 230)),
    }

    def build_home_rows(self) -> list[list[Any]]:
        """Construit les lignes de l'onglet Accueil.

        Args:
            Aucun.

        Returns:
            list[list[Any]]: Lignes de statistiques publiques.
        """

        return [
            ["Plateforme", "Nombre de jeux", "Prix", "Prix moyen"],
            ["Playstation", 2, 57.98, 28.99],
            ["Switch", 2, 89.98, 44.99],
            ["PC", 2, 39.98, 19.99],
            ["Total", 6, 187.94, 31.32],
            ["Date du premier jeu", None, "1997-10-01", None],
            ["Date du dernier jeu", None, "2024-02-15", None],
        ]

    def build_wishlist_rows(self) -> list[list[Any]]:
        """Construit les lignes de l'onglet Liste de souhaits.

        Args:
            Aucun.

        Returns:
            list[list[Any]]: Lignes de souhaits fictifs.
        """

        return [
            self.wishlist_columns,
            ["Projet Aurora", "Playstation", "2025-09-12", "", "", 49.99, "Studio Exemple"],
            ["Pixel Quest 2", "Switch", "2026-03-20", "", "", 39.99, "Indie Lab"],
            ["Nebula Tactics", "PC", "2025-11-05", "", "", 29.99, "Cloud Studio"],
        ]

    def build_platform_rows(self, platform: str) -> list[list[Any]]:
        """Construit les lignes de jeux d'une plateforme.

        Args:
            platform (str): Nom de la plateforme exemple.

        Returns:
            list[list[Any]]: En-tete et jeux fictifs de la plateforme.
        """

        rows_by_platform = {
            "Playstation": [
                [
                    "Crash Bandicoot",
                    "Naughty Dog",
                    "1997-10-01",
                    "2023-05-14",
                    "Magasin exemple",
                    "8/10",
                    24.99,
                    "PAL - FR",
                ],
                [
                    "Gran Turismo",
                    "Polyphony Digital",
                    "1998-05-08",
                    "2023-06-02",
                    "Bourse jeux",
                    "9/10",
                    32.99,
                    "PAL - FR",
                ],
            ],
            "Switch": [
                ["Celeste", "Maddy Makes Games", "2018-01-25", "2024-01-12", "Boutique en ligne", "9/10", 34.99, "FR"],
                ["Hollow Knight", "Team Cherry", "2017-02-24", "2024-02-10", "Magasin exemple", "9/10", 54.99, "FR"],
            ],
            "PC": [
                ["Portal", "Valve", "2007-10-10", "2022-08-04", "Plateforme demat", "10/10", 9.99, "Digital"],
                [
                    "Stardew Valley",
                    "ConcernedApe",
                    "2016-02-26",
                    "2022-09-18",
                    "Plateforme demat",
                    "9/10",
                    29.99,
                    "Digital",
                ],
            ],
        }
        return [self.platform_columns, *rows_by_platform[platform]]
