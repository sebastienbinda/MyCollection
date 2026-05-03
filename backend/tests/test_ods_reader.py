#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import unittest
from unittest.mock import patch

import pandas as pd

from services.ods import OdsCache, OdsReader


class FakeImageReader:
    def list_platform_image_paths(self):
        """Retourne les chemins d'images factices des plateformes.

        Args:
            Aucun.

        Returns:
            dict[str, str]: Images factices indexees par nom d'onglet.
        """

        return {"Switch": "Pictures/switch.png", "Playstation": "Pictures/ps.png"}


class OdsReaderFallbackTest(unittest.TestCase):
    def setUp(self):
        """Prepare un lecteur ODS avec dependances factices.

        Args:
            Aucun.

        Returns:
            None: L'instance de test est initialisee.
        """

        self.reader = OdsReader(
            ods_path="/tmp/fallback-home.ods",
            cache=OdsCache("/tmp/fallback-home.ods"),
            xml_reader=None,
            image_reader=FakeImageReader(),
        )
        self.reader.cache.reset()
        self.reader.list_platforms = lambda: ["Switch", "Playstation"]
        self.reader.read_games_dataframe = self._read_games_dataframe

    def test_home_stats_fallback_recomputes_error_values(self):
        """Verifie le fallback lorsque l'onglet Accueil retourne des erreurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statistiques recalculees.
        """

        with patch("services.ods.ods_reader.pd.read_excel", return_value=self._home_dataframe()):
            stats = self.reader.get_home_stats()

        self.assertEqual(3, stats["totals"]["games_count"])
        self.assertEqual(60.5, stats["totals"]["total_price"])
        self.assertEqual(20.17, stats["totals"]["average_price"])
        self.assertEqual("2019-03-01", stats["first_game_date"])
        self.assertEqual("2021-06-15", stats["last_game_date"])
        self.assertEqual(2, stats["platforms"][0]["games_count"])
        self.assertEqual(30.5, stats["platforms"][0]["total_price"])
        self.assertEqual(15.25, stats["platforms"][0]["average_price"])

    def test_home_stats_keeps_valid_sheet_values(self):
        """Verifie que le fallback ne remplace pas les valeurs Accueil valides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la priorite des valeurs de l'onglet Accueil.
        """

        dataframe = self._home_dataframe()
        dataframe.loc[dataframe["Plateforme"] == "Switch", "Nombre de jeux"] = 99
        dataframe.loc[dataframe["Plateforme"] == "Switch", "Prix"] = 1234
        dataframe.loc[dataframe["Plateforme"] == "Switch", "Prix moyen"] = 12.46

        with patch("services.ods.ods_reader.pd.read_excel", return_value=dataframe):
            stats = self.reader.get_home_stats()

        switch_stats = stats["platforms"][0]
        self.assertEqual(99, switch_stats["games_count"])
        self.assertEqual(1234, switch_stats["total_price"])
        self.assertEqual(12.46, switch_stats["average_price"])

    def _home_dataframe(self):
        """Construit un DataFrame Accueil avec erreurs de formules.

        Args:
            Aucun.

        Returns:
            pandas.DataFrame: Donnees factices de l'onglet Accueil.
        """

        return pd.DataFrame(
            [
                {
                    "Plateforme": "Switch",
                    "Nombre de jeux": "Err:510",
                    "Prix": "Err:510",
                    "Prix moyen": "Err:510",
                },
                {
                    "Plateforme": "Playstation",
                    "Nombre de jeux": "Err:510",
                    "Prix": "Err:510",
                    "Prix moyen": "Err:510",
                },
                {
                    "Plateforme": "Total",
                    "Nombre de jeux": "Err:510",
                    "Prix": "Err:510",
                    "Prix moyen": "Err:510",
                },
                {"Plateforme": "Date du premier jeu", "Prix": "Err:510"},
                {"Plateforme": "Date du dernier jeu", "Prix": "Err:510"},
            ]
        )

    def _read_games_dataframe(self, platform):
        """Retourne les jeux factices d'une plateforme.

        Args:
            platform (str): Nom de l'onglet plateforme.

        Returns:
            pandas.DataFrame: Jeux factices de la plateforme.
        """

        games_by_platform = {
            "Switch": pd.DataFrame(
                [
                    {
                        "Nom du jeu": "Zelda",
                        "Prix d'achat": "10,50",
                        "Date de sortie": "2020-01-01",
                    },
                    {
                        "Nom du jeu": "Mario",
                        "Prix d'achat": 20,
                        "Date de sortie": "2021-06-15",
                    },
                ]
            ),
            "Playstation": pd.DataFrame(
                [
                    {
                        "Nom du jeu": "Gran Turismo",
                        "Prix d'achat": 30,
                        "Date de sortie": "2019-03-01",
                    }
                ]
            ),
        }
        return games_by_platform[platform]


if __name__ == "__main__":
    unittest.main()
