#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import copy
import os
import shutil
from datetime import datetime
from typing import Any, Optional
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET

from .ods_archive_reader import OdsArchiveReader
from .ods_namespaces import OdsNamespaces
from .ods_xml_reader import OdsXmlReader


class OdsWriter:
    def __init__(self, ods_path: str, archive_reader: OdsArchiveReader, xml_reader: OdsXmlReader):
        """Initialise l'ecrivain de contenu ODS.

        Args:
            ods_path (str): Chemin du fichier ODS.
            archive_reader (OdsArchiveReader): Lecteur des fichiers internes ODS.
            xml_reader (OdsXmlReader): Lecteur XML partage.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = ods_path
        self.archive_reader = archive_reader
        self.xml_reader = xml_reader
        self.namespaces = OdsNamespaces.values

    def add_game(self, platform: str, game: dict[str, Any]) -> None:
        """Ajoute un jeu dans le contenu XML de l'ODS.

        Args:
            platform (str): Onglet ODS dans lequel inserer le jeu.
            game (dict[str, Any]): Donnees du jeu deja validees et nettoyees.

        Returns:
            None: Le fichier ODS est modifie sur disque.
        """

        content = self._build_content_with_added_game(platform=platform, game=game)
        self._write_ods_content(content)

    def _build_content_with_added_game(self, platform: str, game: dict[str, Any]) -> bytes:
        """Construit un nouveau `content.xml` avec une ligne de jeu ajoutee.

        Args:
            platform (str): Onglet ODS dans lequel inserer le jeu.
            game (dict[str, Any]): Donnees du jeu deja validees et nettoyees.

        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.
        """

        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, platform)
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
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

    def _find_stats_row_index(self, rows: list[ET.Element]) -> Optional[int]:
        """Trouve l'index de la ligne qui marque la zone de statistiques.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.

        Returns:
            Optional[int]: Index de la ligne contenant `Nombre de Jeux`, sinon `None`.
        """

        for index, row in enumerate(rows):
            if "Nombre de Jeux" in self.xml_reader.row_text_values(row):
                return index
        return None

    def _find_last_game_row_index(self, rows: list[ET.Element], stats_row_index: int) -> Optional[int]:
        """Trouve la derniere ligne de jeu avant les statistiques.

        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.
            stats_row_index (int): Index de debut de la zone de statistiques.

        Returns:
            Optional[int]: Index de la derniere ligne contenant un nom de jeu, sinon `None`.
        """

        last_game_row_index = None
        for index in range(6, stats_row_index):
            cells = self.xml_reader.expanded_cells(rows[index])
            game_name = self.xml_reader.cell_text_value(cells[5]) if len(cells) > 5 else None
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

        cells = self.xml_reader.expanded_cells(row)
        while len(cells) < 13:
            cells.append(ET.Element(f"{{{self.namespaces['table']}}}table-cell"))

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

    def _set_cell_value(self, cell: ET.Element, value_type: str, value: Any) -> None:
        """Ecrit une valeur dans une cellule XML ODS.

        Args:
            cell (xml.etree.ElementTree.Element): Cellule a modifier.
            value_type (str): Type attendu, par exemple `string`, `date` ou `float`.
            value (Any): Valeur brute a ecrire.

        Returns:
            None: La cellule XML est modifiee en place.
        """

        office_value_type = f"{{{self.namespaces['office']}}}value-type"
        office_value = f"{{{self.namespaces['office']}}}value"
        office_date_value = f"{{{self.namespaces['office']}}}date-value"
        calcext_value_type = f"{{{self.namespaces['calcext']}}}value-type"
        table_formula = f"{{{self.namespaces['table']}}}formula"

        for attribute in [office_value_type, office_value, office_date_value, calcext_value_type, table_formula]:
            cell.attrib.pop(attribute, None)
        for child in list(cell):
            cell.remove(child)

        text_value = "" if value is None else str(value).strip()
        if not text_value:
            return

        if value_type == "date" and self._is_iso_date(text_value):
            cell.attrib[office_value_type] = "date"
            cell.attrib[office_date_value] = text_value
            cell.attrib[calcext_value_type] = "date"
        elif value_type == "float" and self._is_number(text_value):
            cell.attrib[office_value_type] = "float"
            cell.attrib[office_value] = text_value.replace(",", ".")
            cell.attrib[calcext_value_type] = "float"
        else:
            cell.attrib[office_value_type] = "string"
            cell.attrib[calcext_value_type] = "string"

        paragraph = ET.SubElement(cell, f"{{{self.namespaces['text']}}}p")
        paragraph.text = text_value

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
