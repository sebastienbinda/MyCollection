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

from services.ods import OdsCache


class OdsCacheTest(unittest.TestCase):
    def test_remember_calls_factory_once_for_same_key(self):
        """Verifie que le cache reutilise la valeur deja construite.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        cache = OdsCache("/tmp/test-cache.ods")
        cache.reset()
        calls = {"count": 0}

        def build_value():
            """Construit une valeur de test pour le cache.

            Args:
                Aucun.

            Returns:
                dict[str, list[int]]: Valeur mutable de test.
            """

            calls["count"] += 1
            return {"items": [1]}

        first_value = cache.remember("games", build_value)
        first_value["items"].append(2)
        second_value = cache.remember("games", build_value)

        self.assertEqual(1, calls["count"])
        self.assertEqual({"items": [1]}, second_value)

    def test_reset_removes_entries_for_current_file(self):
        """Verifie la suppression des entrees d'un fichier ODS.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        cache = OdsCache("/tmp/test-reset.ods")
        cache.reset()
        cache.remember("platforms", lambda: ["Switch"])

        self.assertEqual(1, cache.reset())
        self.assertEqual(0, cache.reset())


if __name__ == "__main__":
    unittest.main()
