from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional, Union


@dataclass
class JeuVideo:
    nom_du_jeu: Optional[str]
    studio: Optional[str]
    date_de_sortie: Optional[Union[date, datetime, str]]
    date_d_achat: Optional[Union[date, datetime, str]]
    lieu_d_achat: Optional[str]
    note: Optional[str]
    prix_d_achat: Optional[Union[float, int, str]]
    version: Optional[str]

    @classmethod
    def from_sheet_row(cls, row: dict[str, Any]) -> "JeuVideo":
        return cls(
            nom_du_jeu=_clean_value(row.get("Nom du jeu")),
            studio=_clean_value(row.get("Studio")),
            date_de_sortie=_clean_value(row.get("Date de sortie")),
            date_d_achat=_clean_value(row.get("Date d'achat") or row.get("Date d’achat")),
            lieu_d_achat=_clean_value(
                row.get("Lieu d'achat") or row.get("Lieu d’achat")
            ),
            note=_clean_value(row.get("Note")),
            prix_d_achat=_clean_value(
                row.get("Prix d'achat") or row.get("Prix d’achat")
            ),
            version=_clean_value(row.get("Version")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "Nom du jeu": self.nom_du_jeu,
            "Studio": self.studio,
            "Date de sortie": _serialize_value(self.date_de_sortie),
            "Date d'achat": _serialize_value(self.date_d_achat),
            "Lieu d'achat": self.lieu_d_achat,
            "Note": self.note,
            "Prix d'achat": _serialize_value(self.prix_d_achat),
            "Version": self.version,
        }


def _clean_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    return value


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
