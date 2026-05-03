#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from dataclasses import dataclass


@dataclass
class Film:
    """Represente un film simple expose par l'API d'exemple.

    Attributes:
        id (int): Identifiant unique du film.
        name (str): Nom lisible du film.
    """

    id: int
    name: str

    def to_dict(self) -> dict[str, object]:
        """Convertit le film en dictionnaire serialisable en JSON.

        Args:
            Aucun.

        Returns:
            dict[str, int | str]: Dictionnaire contenant `id` et `name`.
        """

        return {"id": self.id, "name": self.name}
