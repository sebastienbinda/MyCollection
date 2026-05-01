from dataclasses import dataclass


@dataclass
class Film:
    id: int
    name: str

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}
