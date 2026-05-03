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

import app as app_module


class FakeJeuVideoService:
    def __init__(self):
        """Initialise un service JeuxVideo factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

    def list_platforms(self):
        """Retourne les plateformes factices.

        Args:
            Aucun.

        Returns:
            list[str]: Plateformes disponibles.
        """

        return ["Switch", "Playstation"]

    def reset_cache(self):
        """Retourne un nombre factice d'entrees supprimees.

        Args:
            Aucun.

        Returns:
            int: Nombre d'entrees supprimees.
        """

        return 2

    def search(self, platform, query=""):
        """Retourne les jeux factices d'une plateforme.

        Args:
            platform (str): Plateforme demandee.
            query (str): Recherche optionnelle.

        Returns:
            list[dict[str, str]]: Jeux factices.
        """

        return [{"Nom du jeu": "Mario Kart", "Plateforme": platform, "Query": query}]

    def add_game(self, payload):
        """Retourne le jeu ajoute sans modifier de fichier.

        Args:
            payload (dict[str, str]): Donnees du jeu.

        Returns:
            dict[str, str]: Jeu ajoute.
        """

        if not payload.get("Nom du jeu"):
            raise ValueError("Le nom du jeu est obligatoire.")
        return {"Plateforme": payload.get("platform"), "Nom du jeu": payload.get("Nom du jeu")}


class AppRoutesTest(unittest.TestCase):
    def setUp(self):
        """Remplace le service ODS par un service factice.

        Args:
            Aucun.

        Returns:
            None: Le client Flask est prepare pour chaque test.
        """

        self.original_service = app_module.JeuVideoService
        app_module.JeuVideoService = FakeJeuVideoService
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()

    def tearDown(self):
        """Restaure le service ODS original.

        Args:
            Aucun.

        Returns:
            None: Les modifications globales du test sont annulees.
        """

        app_module.JeuVideoService = self.original_service

    def test_platforms_route_returns_platforms(self):
        """Verifie l'endpoint de liste des plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.get("/collections/JeuxVideo/platforms")

        self.assertEqual(200, response.status_code)
        self.assertEqual(["Switch", "Playstation"], response.get_json()["platforms"])

    def test_cache_reset_route_returns_removed_entries(self):
        """Verifie l'endpoint de reset du cache.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.post("/collections/JeuxVideo/cache/reset")

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.get_json()["removed_entries"])

    def test_add_game_route_returns_created_item(self):
        """Verifie l'endpoint d'ajout d'un jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.post(
            "/collections/JeuxVideo/games",
            json={"platform": "Switch", "Nom du jeu": "Metroid"},
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual("Metroid", response.get_json()["item"]["Nom du jeu"])

    def test_add_game_route_returns_validation_error(self):
        """Verifie la propagation des erreurs de validation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la reponse HTTP.
        """

        response = self.client.post("/collections/JeuxVideo/games", json={"platform": "Switch"})

        self.assertEqual(400, response.status_code)
        self.assertIn("obligatoire", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
