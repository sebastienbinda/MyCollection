from enum import Enum


class CollectionTypes(str, Enum):
    """Types de collections exposes par l'API.

    Valeurs:
        JeuxVideo (str): Collection lue depuis le fichier ODS de jeux video.
        Films (str): Collection d'exemple stockee en memoire.
    """

    JeuxVideo = "JeuxVideo"
    Films = "Films"
