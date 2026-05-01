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
