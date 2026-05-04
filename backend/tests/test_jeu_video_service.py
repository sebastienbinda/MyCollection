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
import unittest

import pandas as pd

from services.jeux_video import JeuVideoService


class FakeReader:
    def __init__(self):
        """Initialise un lecteur ODS factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.platforms = ["Switch", "Playstation"]
        self.games_by_platform = {
            "Switch": pd.DataFrame(
                [
                    {"Nom du jeu": "Mario Kart", "Studio": "Nintendo"},
                    {"Nom du jeu": "Zelda", "Studio": "Nintendo"},
                ]
            ),
            "Playstation": pd.DataFrame(
                [{"Nom du jeu": "Gran Turismo", "Studio": "Polyphony"}]
            ),
            "Liste de souhaits": pd.DataFrame(
                [{"Nom du jeu": "Chrono Trigger", "Console": "Switch 2", "Prix": 60}]
            ),
        }

    def read_games_dataframe(self, platform):
        """Retourne un DataFrame de jeux pour une plateforme.

        Args:
            platform (str): Nom de la plateforme demandee.

        Returns:
            pandas.DataFrame: Jeux associes a la plateforme.
        """

        return self.games_by_platform[platform]

    def list_platforms(self):
        """Retourne les plateformes disponibles.

        Args:
            Aucun.

        Returns:
            list[str]: Plateformes factices.
        """

        return self.platforms


class FakeWriter:
    def __init__(self):
        """Initialise un ecrivain ODS factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.added_games = []
        self.deleted_games = []
        self.deleted_wishlist_games = []

    def add_game(self, platform, game):
        """Enregistre l'ajout d'un jeu sans ecrire de fichier.

        Args:
            platform (str): Plateforme cible.
            game (dict[str, object]): Donnees du jeu.

        Returns:
            None: Les donnees sont conservees en memoire.
        """

        self.added_games.append((platform, game))

    def delete_game(self, platform, game):
        """Enregistre la suppression d'un jeu sans ecrire de fichier.

        Args:
            platform (str): Plateforme cible.
            game (dict[str, object]): Donnees du jeu.

        Returns:
            None: Les donnees sont conservees en memoire.
        """

        self.deleted_games.append((platform, game))

    def delete_wishlist_game(self, game_name, console):
        """Enregistre la suppression wishlist sans ecrire de fichier.

        Args:
            game_name (str): Nom du jeu a supprimer.
            console (str): Console associee.

        Returns:
            None: Les donnees sont conservees en memoire.
        """

        self.deleted_wishlist_games.append((game_name, console))


class FakeCache:
    def __init__(self):
        """Initialise un cache factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.reset_count = 0

    def reset(self):
        """Compte les demandes de reset.

        Args:
            Aucun.

        Returns:
            int: Nombre arbitraire d'entrees supprimees.
        """

        self.reset_count += 1
        return 3


class JeuVideoServiceTest(unittest.TestCase):
    def setUp(self):
        """Prepare une facade de service avec dependances factices.

        Args:
            Aucun.

        Returns:
            None: L'instance est stockee sur le test.
        """

        self.service = JeuVideoService.__new__(JeuVideoService)
        self.service.reader = FakeReader()
        self.service.writer = FakeWriter()
        self.service.cache = FakeCache()

    def test_search_filters_games_by_query(self):
        """Verifie la recherche filtree sur une plateforme.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        results = self.service.search("Switch", "zel")

        self.assertEqual(1, len(results))
        self.assertEqual("Zelda", results[0]["Nom du jeu"])

    def test_search_wishlist_keeps_raw_columns(self):
        """Verifie que la liste de souhaits conserve ses colonnes specifiques.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        results = self.service.search("Liste de souhaits")

        self.assertEqual(1, len(results))
        self.assertEqual("Switch 2", results[0]["Console"])
        self.assertEqual(60, results[0]["Prix"])

    def test_search_by_game_name_scans_all_platforms(self):
        """Verifie la recherche globale par nom de jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        results = self.service.search_by_game_name("turismo")

        self.assertEqual(1, len(results))
        self.assertEqual("Playstation", results[0]["Plateforme"])
        self.assertEqual("Gran Turismo", results[0]["Nom du jeu"])

    def test_add_game_writes_clean_payload_and_resets_cache(self):
        """Verifie l'ajout d'un jeu et l'invalidation du cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        item = self.service.add_game(
            {
                "platform": "Switch",
                "Nom du jeu": " Metroid Prime ",
                "Studio": " Retro Studios ",
            }
        )

        self.assertEqual("Switch", item["Plateforme"])
        self.assertEqual("Metroid Prime", item["Nom du jeu"])
        self.assertEqual(1, self.service.cache.reset_count)
        self.assertEqual("Retro Studios", self.service.writer.added_games[0][1]["Studio"])

    def test_add_game_rejects_unknown_platform(self):
        """Verifie la validation de la plateforme avant ecriture.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        with self.assertRaises(ValueError):
            self.service.add_game({"platform": "Xbox", "Nom du jeu": "Halo"})

    def test_delete_wishlist_game_resets_cache(self):
        """Verifie la suppression d'un jeu wishlist et l'invalidation du cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        item = self.service.delete_wishlist_game(
            {"Nom du jeu": " Chrono Trigger ", "Console": " Switch 2 "}
        )

        self.assertEqual({"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"}, item)
        self.assertEqual(1, self.service.cache.reset_count)
        self.assertEqual(
            [("Chrono Trigger", "Switch 2")],
            self.service.writer.deleted_wishlist_games,
        )

    def test_delete_game_writes_clean_payload_and_resets_cache(self):
        """Verifie la suppression d'un jeu et l'invalidation du cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        item = self.service.delete_game(
            {
                "platform": "Switch",
                "Nom du jeu": " Mario Kart ",
                "Studio": " Nintendo ",
            }
        )

        self.assertEqual("Switch", item["Plateforme"])
        self.assertEqual("Mario Kart", item["Nom du jeu"])
        self.assertEqual(1, self.service.cache.reset_count)
        self.assertEqual("Nintendo", self.service.writer.deleted_games[0][1]["Studio"])

    def test_delete_game_rejects_missing_name(self):
        """Verifie la validation du nom avant suppression.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        with self.assertRaises(ValueError):
            self.service.delete_game({"platform": "Switch"})

    def test_delete_wishlist_game_requires_console(self):
        """Verifie la validation des donnees de suppression wishlist.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        with self.assertRaises(ValueError):
            self.service.delete_wishlist_game({"Nom du jeu": "Chrono Trigger"})


if __name__ == "__main__":
    unittest.main()
