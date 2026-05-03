#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from enum import Enum


class CollectionTypes(str, Enum):
    """Types de collections exposes par l'API.

    Valeurs:
        JeuxVideo (str): Collection lue depuis le fichier ODS de jeux video.
        Films (str): Collection d'exemple stockee en memoire.
    """

    JeuxVideo = "JeuxVideo"
    Films = "Films"
