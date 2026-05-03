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
from typing import Any, Optional


class SheetValueFormatter:
    @staticmethod
    def clean_text(value: Any) -> Optional[str]:
        """Nettoie une valeur de formulaire en texte optionnel.

        Args:
            value (Any): Valeur brute issue du payload JSON.

        Returns:
            Optional[str]: Texte sans espaces en bordure, ou `None` si vide.
        """

        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def serialize(value: Any) -> Any:
        """Serialise une valeur issue du tableur pour JSON.

        Args:
            value (Any): Valeur pandas, Python native, date ou cellule vide.

        Returns:
            Any: Valeur compatible JSON, avec dates ISO et `NaN` converti en `None`.
        """

        if value is None:
            return None
        if isinstance(value, float) and value != value:
            return None
        if isinstance(value, str) and value.strip().lower().startswith("err:"):
            return None
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if hasattr(value, "item"):
            return value.item()
        return value

    @staticmethod
    def normalize_platform_name(value: str) -> str:
        """Normalise un nom de plateforme pour une comparaison souple.

        Args:
            value (str): Nom de plateforme brut.

        Returns:
            str: Nom en minuscules sans espaces.
        """

        return "".join(str(value).lower().split())
