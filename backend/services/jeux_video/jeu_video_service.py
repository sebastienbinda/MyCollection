#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
from typing import Any, Optional

from models import JeuVideo
from services.formatting import SheetValueFormatter
from services.ods import (
    OdsArchiveReader,
    OdsCache,
    OdsImageReader,
    OdsNamespaces,
    OdsPathResolver,
    OdsReader,
    OdsWriter,
    OdsXmlReader,
)


class JeuVideoService:
    def __init__(self, ods_path: Optional[str] = None):
        """Initialise le service d'acces au fichier ODS.

        Args:
            ods_path (Optional[str]): Chemin explicite vers le fichier ODS. Si absent,
                le chemin est resolu depuis `JEUXVIDEO_ODS_PATH` ou les emplacements par defaut.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        OdsNamespaces.register()
        self.ods_path = OdsPathResolver(ods_path).resolve()
        self.cache = OdsCache(self.ods_path)
        self.archive_reader = OdsArchiveReader(self.ods_path, self.cache)
        self.xml_reader = OdsXmlReader(self.archive_reader, self.cache)
        self.image_reader = OdsImageReader(self.archive_reader, self.cache)
        self.reader = OdsReader(self.ods_path, self.cache, self.xml_reader, self.image_reader)
        self.writer = OdsWriter(self.ods_path, self.archive_reader, self.xml_reader)

    def search(self, platform: str, query: str = "") -> list[dict]:
        """Recherche les jeux d'une plateforme.

        Args:
            platform (str): Nom de l'onglet ODS representant la plateforme.
            query (str): Texte optionnel filtre sur toutes les valeurs d'un jeu.

        Returns:
            list[dict]: Liste de jeux serialises pour l'API.
        """

        dataframe = self.reader.read_games_dataframe(platform)
        items = [
            JeuVideo.from_sheet_row(record)
            for record in dataframe.to_dict(orient="records")
        ]

        normalized_query = query.strip().lower()
        if normalized_query:
            items = [
                item
                for item in items
                if normalized_query
                in " ".join(str(value).lower() for value in item.to_dict().values())
            ]
        return [item.to_dict() for item in items]

    def search_by_game_name(self, query: str, limit: int = 50) -> list[dict]:
        """Recherche un nom de jeu dans toutes les plateformes.

        Args:
            query (str): Texte a rechercher dans la colonne `Nom du jeu`.
            limit (int): Nombre maximal de resultats a retourner.

        Returns:
            list[dict]: Jeux trouves, enrichis avec la cle `Plateforme`.
        """

        normalized_query = query.strip().lower()
        if not normalized_query:
            return []

        results = []
        for platform in self.list_platforms():
            for game in self.search(platform=platform):
                game_name = game.get("Nom du jeu")
                if game_name and normalized_query in str(game_name).lower():
                    results.append({"Plateforme": platform, **game})
                    if len(results) >= limit:
                        return results
        return results

    def add_game(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Ajoute un jeu dans l'onglet de plateforme demande.

        Args:
            payload (dict[str, Any]): Donnees du formulaire frontend. Attend notamment
                `platform` (str) et `Nom du jeu` (str).

        Returns:
            dict[str, Any]: Jeu ajoute, enrichi avec `Plateforme`.
        """

        platform = SheetValueFormatter.clean_text(payload.get("platform"))
        game_name = SheetValueFormatter.clean_text(payload.get("Nom du jeu"))
        if not platform:
            raise ValueError("La plateforme est obligatoire.")
        if platform not in self.list_platforms():
            raise ValueError(f"Sheet '{platform}' not found in ODS file.")
        if not game_name:
            raise ValueError("Le nom du jeu est obligatoire.")

        game = self._build_game_payload(payload, game_name)
        self.writer.add_game(platform=platform, game=game)
        self.reset_cache()
        return {"Plateforme": platform, **game}

    def reset_cache(self) -> int:
        """Vide le cache des donnees lues depuis le fichier ODS.

        Args:
            Aucun.

        Returns:
            int: Nombre d'entrees de cache supprimees.
        """

        return self.cache.reset()

    def list_platforms(self) -> list[str]:
        """Liste les onglets ODS correspondant a des plateformes.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets, hors `Accueil` et `Liste de souhaits`.
        """

        return self.reader.list_platforms()

    def get_home_stats(self) -> dict[str, Any]:
        """Lit les statistiques de l'onglet `Accueil`.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Titre, plateformes, totaux, premiere date et derniere date.
        """

        return self.reader.get_home_stats()

    def list_column_values(self, platform: str) -> dict[str, list[str]]:
        """Retourne les valeurs distinctes de chaque colonne d'une plateforme.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            dict[str, list[str]]: Dictionnaire `nom_colonne -> valeurs uniques triees`.
        """

        return self.reader.list_column_values(platform)

    def get_platform_image(self, platform: str) -> tuple[bytes, str, str]:
        """Retourne l'image embarquee dans l'onglet d'une plateforme.

        Args:
            platform (str): Nom exact ou normalise de la plateforme recherchee.

        Returns:
            tuple[bytes, str, str]: Contenu binaire, MIME type et nom de fichier de l'image.
        """

        return self.image_reader.get_platform_image(platform)

    def _build_game_payload(self, payload: dict[str, Any], game_name: str) -> dict[str, Any]:
        """Construit le dictionnaire de jeu nettoye pour l'ecriture ODS.

        Args:
            payload (dict[str, Any]): Donnees brutes du formulaire frontend.
            game_name (str): Nom du jeu deja valide.

        Returns:
            dict[str, Any]: Donnees de jeu nettoyees et pretes a ecrire.
        """

        return {
            "Nom du jeu": game_name,
            "Studio": SheetValueFormatter.clean_text(payload.get("Studio")),
            "Date de sortie": SheetValueFormatter.clean_text(payload.get("Date de sortie")),
            "Date d'achat": SheetValueFormatter.clean_text(payload.get("Date d'achat")),
            "Lieu d'achat": SheetValueFormatter.clean_text(payload.get("Lieu d'achat")),
            "Note": SheetValueFormatter.clean_text(payload.get("Note")),
            "Prix d'achat": SheetValueFormatter.clean_text(payload.get("Prix d'achat")),
            "Version": SheetValueFormatter.clean_text(payload.get("Version")),
        }
