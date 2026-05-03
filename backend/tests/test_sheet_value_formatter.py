#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from datetime import date, datetime
import unittest

from services.formatting import SheetValueFormatter


class SheetValueFormatterTest(unittest.TestCase):
    def test_clean_text_returns_none_for_empty_values(self):
        """Verifie le nettoyage des valeurs texte vides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        self.assertIsNone(SheetValueFormatter.clean_text(None))
        self.assertIsNone(SheetValueFormatter.clean_text("   "))
        self.assertEqual("Mario", SheetValueFormatter.clean_text(" Mario "))

    def test_serialize_converts_dates_and_nan(self):
        """Verifie la serialisation JSON des dates et valeurs NaN.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        self.assertEqual("2026-05-03", SheetValueFormatter.serialize(date(2026, 5, 3)))
        self.assertEqual(
            "2026-05-03T10:15:00",
            SheetValueFormatter.serialize(datetime(2026, 5, 3, 10, 15)),
        )
        self.assertIsNone(SheetValueFormatter.serialize(float("nan")))
        self.assertIsNone(SheetValueFormatter.serialize("Err:510"))
        self.assertEqual("Switch", SheetValueFormatter.serialize("Switch"))

    def test_normalize_platform_name_ignores_case_and_spaces(self):
        """Verifie la normalisation des noms de plateformes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le comportement attendu.
        """

        self.assertEqual(
            "playstation5",
            SheetValueFormatter.normalize_platform_name(" PlayStation 5 "),
        )


if __name__ == "__main__":
    unittest.main()
