"""Exports publics des services backend.

Ce module expose `JeuVideoService`, le service responsable de la lecture,
de la recherche et de l'ecriture dans le fichier ODS.
"""

from .jeu_video_service import JeuVideoService

__all__ = ["JeuVideoService"]
