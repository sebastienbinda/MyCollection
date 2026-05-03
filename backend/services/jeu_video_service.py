#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import os
import copy
import shutil
from datetime import date, datetime
from mimetypes import guess_type
from typing import Any, Optional
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

import pandas as pd

from models import JeuVideo


NAMESPACES = {
    "calcext": "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}

for namespace_prefix, namespace_uri in NAMESPACES.items():
    ET.register_namespace(namespace_prefix, namespace_uri)


class JeuVideoService:
    def __init__(self, ods_path: Optional[str] = None):
        """Initialise le service d'acces au fichier ODS.

        Args:
            ods_path (Optional[str]): Chemin explicite vers le fichier ODS. Si absent,
                le chemin est resolu depuis `JEUXVIDEO_ODS_PATH` ou les emplacements par defaut.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path or self._resolve_ods_path()

    def _resolve_ods_path(self) -> str:
        """Determine le chemin du fichier ODS a utiliser.

        Args:
            Aucun.

        Returns:
            str: Chemin absolu existant vers le fichier ODS.

        Raises:
            FileNotFoundError: Si aucun fichier ODS valide n'est trouve.
        """

        env_path = os.getenv("JEUXVIDEO_ODS_PATH")
        candidate_paths = [
            env_path,
            "~/Documents/JeuxVideo-v2.ods",
            "~/Documents/Documents/JeuxVideo-v2.ods",
        ]
        resolved_path = next(
            (
                os.path.expanduser(path)
                for path in candidate_paths
                if path and os.path.exists(os.path.expanduser(path))
            ),
            None,
        )
        if not resolved_path:
            raise FileNotFoundError(
                "ODS file not found. Configure JEUXVIDEO_ODS_PATH to point to JeuxVideo-v2.ods."
            )
        return resolved_path

    def search(self, platform: str, query: str = "") -> list[dict]:
        """Recherche les jeux d'une plateforme.

        Args:
            platform (str): Nom de l'onglet ODS representant la plateforme.
            query (str): Texte optionnel filtre sur toutes les valeurs d'un jeu.

        Returns:
            list[dict]: Liste de jeux serialises pour l'API.
        """

        dataframe = self._read_games_dataframe(platform)
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
                if not game_name:
                    continue

                if normalized_query in str(game_name).lower():
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

        Raises:
            ValueError: Si la plateforme ou le nom du jeu est absent/invalide.
            FileNotFoundError: Si le fichier ODS n'existe pas.
        """

        platform = _clean_text(payload.get("platform"))
        game_name = _clean_text(payload.get("Nom du jeu"))
        if not platform:
            raise ValueError("La plateforme est obligatoire.")
        if platform not in self.list_platforms():
            raise ValueError(f"Sheet '{platform}' not found in ODS file.")
        if not game_name:
            raise ValueError("Le nom du jeu est obligatoire.")

        game = {
            "Nom du jeu": game_name,
            "Studio": _clean_text(payload.get("Studio")),
            "Date de sortie": _clean_text(payload.get("Date de sortie")),
            "Date d'achat": _clean_text(payload.get("Date d'achat")),
            "Lieu d'achat": _clean_text(payload.get("Lieu d'achat")),
            "Note": _clean_text(payload.get("Note")),
            "Prix d'achat": _clean_text(payload.get("Prix d'achat")),
            "Version": _clean_text(payload.get("Version")),
        }

        content = self._build_content_with_added_game(platform=platform, game=game)
        self._write_ods_content(content)
        return {"Plateforme": platform, **game}

    def list_platforms(self) -> list[str]:
        """Liste les onglets ODS correspondant a des plateformes.

        Args:
            Aucun.

        Returns:
            list[str]: Noms des onglets, hors `Accueil` et `Liste de souhaits`.
        """

        excel_file = pd.ExcelFile(self.ods_path, engine="odf")
        excluded_sheets = {"Accueil", "Liste de souhaits"}
        return [sheet for sheet in excel_file.sheet_names if sheet not in excluded_sheets]

    def get_home_stats(self) -> dict[str, Any]:
        """Lit les statistiques de l'onglet `Accueil`.

        Args:
            Aucun.

        Returns:
            dict[str, Any]: Titre, plateformes, totaux, premiere date et derniere date.

        Raises:
            ValueError: Si l'onglet `Accueil` est absent.
            FileNotFoundError: Si le fichier ODS n'existe pas.
        """

        dataframe = pd.read_excel(
            self.ods_path,
            sheet_name="Accueil",
            engine="odf",
            header=5,
        )
        dataframe = dataframe.where(pd.notna(dataframe), None)

        sheet_names_by_key = {
            self._normalize_platform_name(platform): platform
            for platform in self.list_platforms()
        }
        image_paths_by_sheet = self._list_platform_image_paths()
        platforms = []
        totals: dict[str, Any] = {}
        first_game_date = None
        last_game_date = None

        for row in dataframe.to_dict(orient="records"):
            platform_name = _clean_text(row.get("Plateforme"))
            if not platform_name:
                continue

            if platform_name == "Total":
                totals = {
                    "games_count": _serialize_sheet_value(row.get("Nombre de jeux")),
                    "total_price": _serialize_sheet_value(row.get("Prix")),
                    "average_price": _serialize_sheet_value(row.get("Prix moyen")),
                }
                continue

            if platform_name == "Date du premier jeu":
                first_game_date = _serialize_sheet_value(row.get("Prix"))
                continue

            if platform_name == "Date du dernier jeu":
                last_game_date = _serialize_sheet_value(row.get("Prix"))
                continue

            sheet_name = sheet_names_by_key.get(
                self._normalize_platform_name(platform_name), platform_name
            )
            platforms.append(
                {
                    "name": platform_name,
                    "sheet_name": sheet_name,
                    "image_url": f"/collections/JeuxVideo/platform-image/{sheet_name}",
                    "games_count": _serialize_sheet_value(row.get("Nombre de jeux")),
                    "total_price": _serialize_sheet_value(row.get("Prix")),
                    "average_price": _serialize_sheet_value(row.get("Prix moyen")),
                    "has_image": sheet_name in image_paths_by_sheet,
                }
            )

        return {
            "title": "Collection Jeux Video",
            "platforms": platforms,
            "totals": totals,
            "first_game_date": first_game_date,
            "last_game_date": last_game_date,
        }

    def list_column_values(self, platform: str) -> dict[str, list[str]]:
        """Retourne les valeurs distinctes de chaque colonne d'une plateforme.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            dict[str, list[str]]: Dictionnaire `nom_colonne -> valeurs uniques triees`.
        """

        dataframe = self._read_games_dataframe(platform)

        values_by_column: dict[str, list[str]] = {}
        for column in dataframe.columns:
            unique_values = sorted(
                {
                    str(value).strip()
                    for value in dataframe[column].tolist()
                    if value is not None and str(value).strip() != ""
                }
            )
            values_by_column[str(column)] = unique_values

        return values_by_column

    def _read_games_dataframe(self, platform: str) -> pd.DataFrame:
        """Lit les jeux d'une plateforme dans un DataFrame.

        Args:
            platform (str): Nom de l'onglet ODS a lire.

        Returns:
            pandas.DataFrame: Lignes de jeux avec colonnes normalisees.

        Raises:
            ValueError: Si l'onglet n'existe pas.
        """

        try:
            dataframe = pd.read_excel(
                self.ods_path,
                sheet_name=platform,
                engine="odf",
                header=5,
                usecols="F:M",
            )
            dataframe = dataframe.where(pd.notna(dataframe), None)
            return self._normalize_games_dataframe_columns(dataframe)
        except ValueError:
            if platform not in self.list_platforms():
                raise
            return self._read_games_dataframe_from_xml(platform)

    def _read_games_dataframe_from_xml(self, platform: str) -> pd.DataFrame:
        """Lit les jeux depuis le XML interne de l'ODS en secours de pandas.

        Args:
            platform (str): Nom de l'onglet ODS a parser.

        Returns:
            pandas.DataFrame: Donnees de jeux extraites des colonnes F a M.
        """

        rows = self._read_sheet_rows_from_xml(platform)
        selected_rows = [row[5:13] for row in rows if len(row) >= 6]
        if len(selected_rows) <= 5:
            return pd.DataFrame()

        columns = [
            str(value).strip() if value is not None and str(value).strip() else f"Colonne {index + 1}"
            for index, value in enumerate(selected_rows[5])
        ]
        records = []
        for row in selected_rows[6:]:
            padded_row = row + [None] * (len(columns) - len(row))
            record = {
                column: value
                for column, value in zip(columns, padded_row)
            }
            if any(value is not None and str(value).strip() != "" for value in record.values()):
                records.append(record)

        return self._normalize_games_dataframe_columns(pd.DataFrame(records, columns=columns))

    def _normalize_games_dataframe_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Normalise les noms de colonnes contenant des apostrophes typographiques.

        Args:
            dataframe (pandas.DataFrame): Tableau de jeux lu depuis l'ODS.

        Returns:
            pandas.DataFrame: Tableau avec les noms de colonnes harmonises.
        """

        return dataframe.rename(
            columns={
                "Date d’achat": "Date d'achat",
                "Lieu d’achat": "Lieu d'achat",
                "Prix d’achat": "Prix d'achat",
            }
        )

    def _build_content_with_added_game(self, platform: str, game: dict[str, Any]) -> bytes:
        """Construit un nouveau `content.xml` avec une ligne de jeu ajoutee.

        Args:
            platform (str): Onglet ODS dans lequel inserer le jeu.
            game (dict[str, Any]): Donnees du jeu deja validees et nettoyees.

        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.

        Raises:
            ValueError: Si la zone de statistiques ou une ligne modele est introuvable.
        """

        with ZipFile(self.ods_path) as ods_archive:
            content = ods_archive.read("content.xml")

        root = ET.fromstring(content)
        sheet = self._find_sheet(root, platform)
        row_tag = f"{{{NAMESPACES['table']}}}table-row"
        repeated_rows_attribute = f"{{{NAMESPACES['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = []
        for child in direct_children:
            if child.tag != row_tag:
                continue
            repeated_rows = int(child.attrib.get(repeated_rows_attribute, "1"))
            for _ in range(repeated_rows):
                expanded_row = copy.deepcopy(child)
                expanded_row.attrib.pop(repeated_rows_attribute, None)
                expanded_rows.append(expanded_row)

        stats_row_index = self._find_stats_row_index(expanded_rows)
        if stats_row_index is None:
            raise ValueError(f"Unable to find stats area in sheet '{platform}'.")

        last_game_row_index = self._find_last_game_row_index(expanded_rows, stats_row_index)
        if last_game_row_index is None:
            raise ValueError(f"Unable to find a template row in sheet '{platform}'.")

        target_row_index = last_game_row_index + 1
        template_row = copy.deepcopy(expanded_rows[last_game_row_index])
        self._set_game_row_values(template_row, game)

        if target_row_index < stats_row_index:
            expanded_rows[target_row_index] = template_row
        else:
            expanded_rows.insert(stats_row_index, template_row)

        for child in list(sheet):
            if child.tag == row_tag:
                sheet.remove(child)
        for offset, row in enumerate(expanded_rows):
            sheet.insert(row_insert_position + offset, row)

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _write_ods_content(self, content: bytes) -> None:
        """Ecrit le nouveau `content.xml` dans le fichier ODS.

        Args:
            content (bytes): XML complet de `content.xml` apres modification.

        Returns:
            None: La methode modifie le fichier ODS sur disque.
        """

        backup_path = f"{self.ods_path}.backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(self.ods_path, backup_path)
        tmp_path = f"{self.ods_path}.tmp"

        with ZipFile(self.ods_path, "r") as source_archive:
            with ZipFile(tmp_path, "w", compression=ZIP_DEFLATED) as target_archive:
                for item in source_archive.infolist():
                    if item.filename == "content.xml":
                        target_archive.writestr(item, content)
                    else:
                        target_archive.writestr(item, source_archive.read(item.filename))

        os.replace(tmp_path, self.ods_path)

    def _find_sheet(self, root: ET.Element, sheet_name: str) -> ET.Element:
        """Recherche un onglet dans l'arbre XML de l'ODS.

        Args:
            root (xml.etree.ElementTree.Element): Racine XML de `content.xml`.
            sheet_name (str): Nom exact de l'onglet recherche.

        Returns:
            xml.etree.ElementTree.Element: Element XML de l'onglet.

        Raises:
            ValueError: Si l'onglet n'existe pas.
        """

        table_name_attribute = f"{{{NAMESPACES['table']}}}name"
        sheet = next(
            (
                table
                for table in root.findall(".//table:table", NAMESPACES)
                if table.attrib.get(table_name_attribute) == sheet_name
            ),
            None,
        )
        if sheet is None:
            raise ValueError(f"Sheet '{sheet_name}' not found in ODS file.")
        return sheet

    def _find_stats_row_index(self, rows: list[ET.Element]) -> Optional[int]:
        """Trouve l'index de la ligne qui marque la zone de statistiques.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.

        Returns:
            Optional[int]: Index de la ligne contenant `Nombre de Jeux`, sinon `None`.
        """

        for index, row in enumerate(rows):
            if "Nombre de Jeux" in self._row_text_values(row):
                return index
        return None

    def _find_last_game_row_index(
        self, rows: list[ET.Element], stats_row_index: int
    ) -> Optional[int]:
        """Trouve la derniere ligne de jeu avant les statistiques.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.
            stats_row_index (int): Index de debut de la zone de statistiques.

        Returns:
            Optional[int]: Index de la derniere ligne contenant un nom de jeu, sinon `None`.
        """

        last_game_row_index = None
        for index in range(6, stats_row_index):
            cells = self._expanded_cells(rows[index])
            game_name = self._cell_text_value(cells[5]) if len(cells) > 5 else None
            if game_name:
                last_game_row_index = index
        return last_game_row_index

    def _set_game_row_values(self, row: ET.Element, game: dict[str, Any]) -> None:
        """Remplit les cellules d'une ligne XML avec les donnees d'un jeu.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML clonee depuis une ligne modele.
            game (dict[str, Any]): Donnees du jeu a placer dans les colonnes F a M.

        Returns:
            None: La ligne XML est modifiee en place.
        """

        cells = self._expanded_cells(row)
        while len(cells) < 13:
            cells.append(ET.Element(f"{{{NAMESPACES['table']}}}table-cell"))

        values_by_index = {
            5: ("string", game["Nom du jeu"]),
            6: ("string", game["Studio"]),
            7: ("date", game["Date de sortie"]),
            8: ("date", game["Date d'achat"]),
            9: ("string", game["Lieu d'achat"]),
            10: ("string", game["Note"]),
            11: ("float", game["Prix d'achat"]),
            12: ("string", game["Version"]),
        }
        for index, (value_type, value) in values_by_index.items():
            self._set_cell_value(cells[index], value_type, value)

        for child in list(row):
            row.remove(child)
        for cell in cells:
            row.append(cell)

    def _expanded_cells(self, row: ET.Element) -> list[ET.Element]:
        """Developpe les cellules repetees d'une ligne ODS.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML contenant des cellules ODS.

        Returns:
            list[xml.etree.ElementTree.Element]: Cellules individuelles sans attribut de repetition.
        """

        repeated_columns_attribute = f"{{{NAMESPACES['table']}}}number-columns-repeated"
        cells = []
        for cell in list(row):
            if not cell.tag.endswith("table-cell"):
                continue
            repeated_columns = int(cell.attrib.get(repeated_columns_attribute, "1"))
            for _ in range(repeated_columns):
                expanded_cell = copy.deepcopy(cell)
                expanded_cell.attrib.pop(repeated_columns_attribute, None)
                cells.append(expanded_cell)
        return cells

    def _set_cell_value(self, cell: ET.Element, value_type: str, value: Any) -> None:
        """Ecrit une valeur dans une cellule XML ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule a modifier.
            value_type (str): Type attendu, par exemple `string`, `date` ou `float`.
            value (Any): Valeur brute a ecrire.

        Returns:
            None: La cellule XML est modifiee en place.
        """

        office_value_type = f"{{{NAMESPACES['office']}}}value-type"
        office_value = f"{{{NAMESPACES['office']}}}value"
        office_date_value = f"{{{NAMESPACES['office']}}}date-value"
        calcext_value_type = f"{{{NAMESPACES['calcext']}}}value-type"
        table_formula = f"{{{NAMESPACES['table']}}}formula"

        for attribute in [office_value_type, office_value, office_date_value, calcext_value_type, table_formula]:
            cell.attrib.pop(attribute, None)
        for child in list(cell):
            cell.remove(child)

        if value is None:
            return

        text_value = str(value).strip()
        if not text_value:
            return

        if value_type == "date" and self._is_iso_date(text_value):
            cell.attrib[office_value_type] = "date"
            cell.attrib[office_date_value] = text_value
            cell.attrib[calcext_value_type] = "date"
        elif value_type == "float" and self._is_number(text_value):
            normalized_number = text_value.replace(",", ".")
            cell.attrib[office_value_type] = "float"
            cell.attrib[office_value] = normalized_number
            cell.attrib[calcext_value_type] = "float"
        else:
            cell.attrib[office_value_type] = "string"
            cell.attrib[calcext_value_type] = "string"

        paragraph = ET.SubElement(cell, f"{{{NAMESPACES['text']}}}p")
        paragraph.text = text_value

    def _row_text_values(self, row: ET.Element) -> list[str]:
        """Extrait tous les textes non vides d'une ligne XML ODS.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML a inspecter.

        Returns:
            list[str]: Textes des cellules non vides.
        """

        return [
            value
            for value in (self._cell_text_value(cell) for cell in self._expanded_cells(row))
            if value
        ]

    def _cell_text_value(self, cell: ET.Element) -> Optional[str]:
        """Extrait le texte visible d'une cellule ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule XML a lire.

        Returns:
            Optional[str]: Texte concatene des paragraphes, ou `None` si vide.
        """

        text_parts = []
        for paragraph in cell.findall(".//text:p", NAMESPACES):
            text_parts.append("".join(paragraph.itertext()))
        text = "\n".join(part for part in text_parts if part).strip()
        return text or None

    def _is_iso_date(self, value: str) -> bool:
        """Indique si une chaine respecte le format date ISO `YYYY-MM-DD`.

        Args:
            value (str): Texte a valider.

        Returns:
            bool: `True` si le texte est une date ISO valide, sinon `False`.
        """

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_number(self, value: str) -> bool:
        """Indique si une chaine represente un nombre.

        Args:
            value (str): Texte a valider, avec virgule ou point decimal accepte.

        Returns:
            bool: `True` si le texte est convertible en float, sinon `False`.
        """

        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            return False

    def get_platform_image(self, platform: str) -> tuple[bytes, str, str]:
        """Retourne l'image embarquee dans l'onglet d'une plateforme.

        Args:
            platform (str): Nom exact ou normalise de la plateforme recherchee.

        Returns:
            tuple[bytes, str, str]: Contenu binaire, MIME type et nom de fichier de l'image.

        Raises:
            ValueError: Si aucune image n'est trouvee pour la plateforme.
        """

        image_paths_by_sheet = self._list_platform_image_paths()
        image_path = image_paths_by_sheet.get(platform)
        if not image_path:
            normalized_platform = self._normalize_platform_name(platform)
            image_path = next(
                (
                    path
                    for sheet_name, path in image_paths_by_sheet.items()
                    if self._normalize_platform_name(sheet_name) == normalized_platform
                ),
                None,
            )

        if not image_path:
            raise ValueError(f"No image found for platform '{platform}'.")

        with ZipFile(self.ods_path) as ods_archive:
            image_bytes = ods_archive.read(image_path)

        mime_type = guess_type(image_path)[0] or "application/octet-stream"
        filename = os.path.basename(image_path)
        return image_bytes, mime_type, filename

    def _list_platform_image_paths(self) -> dict[str, str]:
        """Liste les chemins des images embarquees par onglet ODS.

        Args:
            Aucun.

        Returns:
            dict[str, str]: Dictionnaire `nom_onglet -> chemin_image_dans_archive`.
        """

        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
            "xlink": "http://www.w3.org/1999/xlink",
        }
        table_name_attribute = f"{{{namespaces['table']}}}name"
        href_attribute = f"{{{namespaces['xlink']}}}href"
        image_paths: dict[str, str] = {}

        with ZipFile(self.ods_path) as ods_archive:
            content = ods_archive.read("content.xml")

        root = ET.fromstring(content)
        for table in root.findall(".//table:table", namespaces):
            sheet_name = table.attrib.get(table_name_attribute)
            if not sheet_name:
                continue

            image_path = next(
                (
                    image.attrib.get(href_attribute)
                    for image in table.findall(".//draw:image", namespaces)
                    if (image.attrib.get(href_attribute) or "").startswith("Pictures/")
                ),
                None,
            )
            if image_path:
                image_paths[sheet_name] = image_path

        return image_paths

    def _read_sheet_rows_from_xml(self, sheet_name: str) -> list[list[Any]]:
        """Lit toutes les lignes d'un onglet depuis le XML interne de l'ODS.

        Args:
            sheet_name (str): Nom exact de l'onglet a extraire.

        Returns:
            list[list[Any]]: Lignes de cellules avec repetitions ODS developpees.

        Raises:
            ValueError: Si l'onglet demande est absent.
        """

        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }
        table_name_attribute = f"{{{namespaces['table']}}}name"
        repeated_rows_attribute = f"{{{namespaces['table']}}}number-rows-repeated"
        repeated_columns_attribute = f"{{{namespaces['table']}}}number-columns-repeated"
        value_type_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value-type"
        value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value"
        date_value_attribute = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}date-value"

        with ZipFile(self.ods_path) as ods_archive:
            content = ods_archive.read("content.xml")

        root = ET.fromstring(content)
        sheet = next(
            (
                table
                for table in root.findall(".//table:table", namespaces)
                if table.attrib.get(table_name_attribute) == sheet_name
            ),
            None,
        )
        if sheet is None:
            raise ValueError(f"Sheet '{sheet_name}' not found in ODS file.")

        rows = []
        for table_row in sheet.findall("table:table-row", namespaces):
            repeated_rows = int(table_row.attrib.get(repeated_rows_attribute, "1"))
            row_values = []
            for cell in list(table_row):
                if not cell.tag.endswith("table-cell"):
                    continue
                repeated_columns = int(cell.attrib.get(repeated_columns_attribute, "1"))
                value = self._extract_cell_value(
                    cell,
                    value_type_attribute,
                    value_attribute,
                    date_value_attribute,
                    namespaces,
                )
                row_values.extend([value] * repeated_columns)
            for _ in range(repeated_rows):
                rows.append(list(row_values))

        return rows

    def _extract_cell_value(
        self,
        cell: ET.Element,
        value_type_attribute: str,
        value_attribute: str,
        date_value_attribute: str,
        namespaces: dict[str, str],
    ) -> Any:
        """Extrait une valeur Python depuis une cellule XML ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule XML source.
            value_type_attribute (str): Nom qualifie de l'attribut `office:value-type`.
            value_attribute (str): Nom qualifie de l'attribut numerique `office:value`.
            date_value_attribute (str): Nom qualifie de l'attribut date `office:date-value`.
            namespaces (dict[str, str]): Espaces de noms XML utilises pour trouver les paragraphes.

        Returns:
            Any: int, float, str ou `None` selon le contenu de la cellule.
        """

        value_type = cell.attrib.get(value_type_attribute)
        if value_type == "float" and value_attribute in cell.attrib:
            value = float(cell.attrib[value_attribute])
            return int(value) if value.is_integer() else value
        if value_type == "date" and date_value_attribute in cell.attrib:
            return cell.attrib[date_value_attribute]

        text_parts = []
        for paragraph in cell.findall(".//text:p", namespaces):
            text_parts.append("".join(paragraph.itertext()))
        text = "\n".join(part for part in text_parts if part).strip()
        return text or None

    def _normalize_platform_name(self, value: str) -> str:
        """Normalise un nom de plateforme pour une comparaison souple.

        Args:
            value (str): Nom de plateforme brut.

        Returns:
            str: Nom en minuscules sans espaces.
        """

        return "".join(str(value).lower().split())


def _clean_text(value: Any) -> Optional[str]:
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


def _serialize_sheet_value(value: Any) -> Any:
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
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value
