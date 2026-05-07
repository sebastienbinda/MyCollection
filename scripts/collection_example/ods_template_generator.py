#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-07
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : generateur ODS qui conserve les styles du fichier modele.
from __future__ import annotations

import copy
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from collection_example.data import CollectionExampleData
from collection_example.png_builder import ExamplePngBuilder


class StyledCollectionExampleGenerator:
    """Genere un ODS exemple a partir d'un modele style."""

    namespaces = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
        "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
        "xlink": "http://www.w3.org/1999/xlink",
        "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
    }
    platform_names = ["Playstation", "Switch", "PC"]

    def __init__(self, output_path: Path, template_path: Path | None = None):
        """Initialise le generateur style.

        Args:
            output_path (Path): Chemin du fichier exemple a produire.
            template_path (Path | None): Chemin optionnel du modele ODS source.

        Returns:
            None: Le constructeur prepare les chemins et dependances.
        """

        self.output_path = output_path
        self.template_path = template_path or self._find_template_path(output_path)
        self.data = CollectionExampleData()
        self.png_builder = ExamplePngBuilder()

    def generate(self) -> None:
        """Genere le fichier ODS exemple en conservant les styles du modele.

        Args:
            Aucun.

        Returns:
            None: Ecrit le fichier ODS sur disque.
        """

        entries = self._read_archive_entries(self.template_path)
        entries = self._remove_private_binary_entries(entries)
        entries["content.xml"] = self._build_content(entries["content.xml"])
        entries["META-INF/manifest.xml"] = self._build_manifest(entries["META-INF/manifest.xml"])
        self._add_example_images(entries)
        self._write_archive_entries(entries)

    def _find_template_path(self, output_path: Path) -> Path:
        """Trouve le meilleur fichier ODS modele disponible.

        Args:
            output_path (Path): Chemin de sortie demande.

        Returns:
            Path: Chemin du modele ODS a lire.
        """

        for candidate in [Path("collection.ods"), output_path]:
            if candidate.exists():
                return candidate
        raise FileNotFoundError("collection.ods est requis pour generer un exemple style.")

    def _read_archive_entries(self, archive_path: Path) -> dict[str, bytes]:
        """Lit les fichiers internes d'une archive ODS.

        Args:
            archive_path (Path): Chemin de l'archive ODS source.

        Returns:
            dict[str, bytes]: Entrees internes indexees par chemin.
        """

        with zipfile.ZipFile(archive_path, "r") as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def _write_archive_entries(self, entries: dict[str, bytes]) -> None:
        """Ecrit les entrees dans le fichier ODS final.

        Args:
            entries (dict[str, bytes]): Entrees internes a sauvegarder.

        Returns:
            None: Remplace le fichier de sortie.
        """

        with zipfile.ZipFile(self.output_path, "w") as archive:
            archive.writestr(zipfile.ZipInfo("mimetype"), entries["mimetype"], compress_type=zipfile.ZIP_STORED)
            for name, content in entries.items():
                if name != "mimetype":
                    archive.writestr(name, content, compress_type=zipfile.ZIP_DEFLATED)

    def _remove_private_binary_entries(self, entries: dict[str, bytes]) -> dict[str, bytes]:
        """Supprime les images, miniatures et objets embarques du modele.

        Args:
            entries (dict[str, bytes]): Entrees originales du modele.

        Returns:
            dict[str, bytes]: Entrees sans binaires personnels.
        """

        return {
            name: content
            for name, content in entries.items()
            if not self._is_private_binary_entry(name)
        }

    def _is_private_binary_entry(self, name: str) -> bool:
        """Indique si une entree peut contenir du contenu personnel.

        Args:
            name (str): Chemin interne de l'entree ODS.

        Returns:
            bool: `True` si l'entree doit etre exclue de l'exemple.
        """

        return (
            name.startswith("Pictures/")
            or name.startswith("Thumbnails/")
            or name.startswith("ObjectReplacements/")
            or name.startswith("Object ")
            or name == "manifest.rdf"
        )

    def _build_content(self, content: bytes) -> bytes:
        """Construit le contenu XML style avec des donnees exemples.

        Args:
            content (bytes): Contenu XML du modele.

        Returns:
            bytes: Contenu XML anonymise et peuple.
        """

        self._register_namespaces()
        root = ET.fromstring(content)
        spreadsheet = root.find(".//office:spreadsheet", self.namespaces)
        if spreadsheet is None:
            raise ValueError("content.xml ne contient pas de feuille ODS.")
        tables = self._build_example_tables(spreadsheet)
        for table in list(spreadsheet.findall("table:table", self.namespaces)):
            spreadsheet.remove(table)
        for table in tables:
            spreadsheet.append(table)
        return ET.tostring(root, encoding="UTF-8", xml_declaration=True)

    def _build_example_tables(self, spreadsheet: ET.Element) -> list[ET.Element]:
        """Construit les onglets exemples a partir des styles existants.

        Args:
            spreadsheet (xml.etree.ElementTree.Element): Element tableur source.

        Returns:
            list[xml.etree.ElementTree.Element]: Onglets exemples styles.
        """

        source_tables = self._index_tables(spreadsheet)
        platform_template = source_tables.get("Playstation") or next(iter(source_tables.values()))
        specs = [
            ("Accueil", "Accueil", "Collection Jeux Video - Exemple", 0, self.data.build_home_rows()),
            ("Liste de souhaits", "Liste de souhaits", "Liste de souhaits", 5, self.data.build_wishlist_rows()),
            ("Playstation", "Playstation", "Playstation", 5, self.data.build_platform_rows("Playstation")),
            ("Switch", "Switch", "Switch", 5, self.data.build_platform_rows("Switch")),
            ("Xbox", "PC", "PC", 5, self.data.build_platform_rows("PC")),
        ]
        tables = []
        for source_name, target_name, title, start_col, rows in specs:
            source_table = source_tables.get(source_name, platform_template)
            tables.append(self._build_table(source_table, target_name, title, start_col, rows))
        return tables

    def _index_tables(self, spreadsheet: ET.Element) -> dict[str, ET.Element]:
        """Indexe les onglets du modele par nom.

        Args:
            spreadsheet (xml.etree.ElementTree.Element): Element tableur source.

        Returns:
            dict[str, xml.etree.ElementTree.Element]: Onglets indexes.
        """

        name_attr = self._attr("table", "name")
        return {
            table.attrib[name_attr]: table
            for table in spreadsheet.findall("table:table", self.namespaces)
            if table.attrib.get(name_attr)
        }

    def _build_table(
        self,
        source_table: ET.Element,
        target_name: str,
        title: str,
        start_col: int,
        rows: list[list[Any]],
    ) -> ET.Element:
        """Construit un onglet avec les styles d'un onglet source.

        Args:
            source_table (xml.etree.ElementTree.Element): Onglet modele.
            target_name (str): Nom final de l'onglet.
            title (str): Titre visible en A1.
            start_col (int): Colonne de depart des donnees.
            rows (list[list[Any]]): Lignes a ecrire.

        Returns:
            xml.etree.ElementTree.Element: Onglet final.
        """

        table = copy.deepcopy(source_table)
        table.set(self._attr("table", "name"), target_name)
        self._remove_private_drawings(table)
        row_templates = self._extract_row_templates(source_table)
        for row in list(table.findall("table:table-row", self.namespaces)):
            table.remove(row)
        table.append(self._build_row(row_templates, 0, [title]))
        for row_index in range(1, 5):
            table.append(self._build_row(row_templates, row_index, []))
        for row_offset, row_values in enumerate(rows):
            values = [None] * start_col + row_values
            table.append(self._build_row(row_templates, row_offset + 5, values))
        if target_name in self.platform_names:
            self._add_image_to_table(table, target_name, self.data.platform_images[target_name][0])
        return table

    def _remove_private_drawings(self, element: ET.Element) -> None:
        """Supprime les anciens objets graphiques du modele.

        Args:
            element (xml.etree.ElementTree.Element): Element XML a nettoyer.

        Returns:
            None: Modifie recursivement l'element fourni.
        """

        private_tags = {
            self._tag("draw", "frame"),
            self._tag("draw", "image"),
            self._tag("draw", "object"),
            self._tag("draw", "plugin"),
        }
        for child in list(element):
            if child.tag in private_tags:
                element.remove(child)
            else:
                self._remove_private_drawings(child)

    def _extract_row_templates(self, table: ET.Element) -> list[tuple[dict[str, str], list[dict[str, str]]]]:
        """Extrait les styles de lignes et cellules du modele.

        Args:
            table (xml.etree.ElementTree.Element): Onglet source.

        Returns:
            list[tuple[dict[str, str], list[dict[str, str]]]]: Styles reutilisables.
        """

        templates = []
        for row in table.findall("table:table-row", self.namespaces):
            templates.append((self._style_attrs(row), self._extract_cell_templates(row)))
        return templates

    def _extract_cell_templates(self, row: ET.Element) -> list[dict[str, str]]:
        """Extrait les styles de cellules d'une ligne source.

        Args:
            row (xml.etree.ElementTree.Element): Ligne XML source.

        Returns:
            list[dict[str, str]]: Styles de cellules developpes.
        """

        templates = []
        repeat_attr = self._attr("table", "number-columns-repeated")
        for cell in row.findall("table:table-cell", self.namespaces):
            repeat = int(cell.attrib.get(repeat_attr, "1"))
            templates.extend([self._style_attrs(cell)] * min(repeat, 40))
        return templates

    def _build_row(
        self,
        templates: list[tuple[dict[str, str], list[dict[str, str]]]],
        row_index: int,
        values: list[Any],
    ) -> ET.Element:
        """Construit une ligne XML avec styles preserves.

        Args:
            templates (list[tuple[dict[str, str], list[dict[str, str]]]]): Styles source.
            row_index (int): Index de ligne a imiter.
            values (list[Any]): Valeurs a ecrire.

        Returns:
            xml.etree.ElementTree.Element: Ligne ODS.
        """

        row_attrs, cell_templates = self._template_at(templates, row_index)
        row = ET.Element(self._tag("table", "table-row"), row_attrs)
        for col_index, value in enumerate(values):
            row.append(self._build_cell(self._cell_attrs_at(cell_templates, col_index), value))
        return row

    def _build_cell(self, style_attrs: dict[str, str], value: Any) -> ET.Element:
        """Construit une cellule ODS.

        Args:
            style_attrs (dict[str, str]): Attributs de style a conserver.
            value (Any): Valeur de cellule a ecrire.

        Returns:
            xml.etree.ElementTree.Element: Cellule ODS.
        """

        cell = ET.Element(self._tag("table", "table-cell"), dict(style_attrs))
        if value is None or value == "":
            return cell
        if isinstance(value, (int, float)):
            cell.set(self._attr("office", "value-type"), "float")
            cell.set(self._attr("office", "value"), str(value))
        else:
            cell.set(self._attr("office", "value-type"), "string")
            cell.set(self._attr("office", "string-value"), str(value))
        paragraph = ET.SubElement(cell, self._tag("text", "p"))
        paragraph.text = str(value)
        return cell

    def _template_at(
        self,
        templates: list[tuple[dict[str, str], list[dict[str, str]]]],
        row_index: int,
    ) -> tuple[dict[str, str], list[dict[str, str]]]:
        """Retourne le style de ligne le plus proche.

        Args:
            templates (list[tuple[dict[str, str], list[dict[str, str]]]]): Styles source.
            row_index (int): Index de ligne cible.

        Returns:
            tuple[dict[str, str], list[dict[str, str]]]: Style de ligne et cellules.
        """

        if not templates:
            return {}, []
        return templates[min(row_index, len(templates) - 1)]

    def _cell_attrs_at(self, templates: list[dict[str, str]], col_index: int) -> dict[str, str]:
        """Retourne le style de cellule le plus proche.

        Args:
            templates (list[dict[str, str]]): Styles de cellules source.
            col_index (int): Index de colonne cible.

        Returns:
            dict[str, str]: Attributs de style.
        """

        if not templates:
            return {}
        return dict(templates[min(col_index, len(templates) - 1)])

    def _style_attrs(self, element: ET.Element) -> dict[str, str]:
        """Conserve uniquement les attributs de style non personnels.

        Args:
            element (xml.etree.ElementTree.Element): Element source.

        Returns:
            dict[str, str]: Attributs de style conserves.
        """

        allowed_names = {"style-name", "default-cell-style-name", "visibility"}
        return {key: value for key, value in element.attrib.items() if key.split("}")[-1] in allowed_names}

    def _add_image_to_table(self, table: ET.Element, sheet_name: str, image_path: str) -> None:
        """Ajoute une image exemple a un onglet plateforme.

        Args:
            table (xml.etree.ElementTree.Element): Onglet cible.
            sheet_name (str): Nom de la plateforme.
            image_path (str): Chemin interne de l'image.

        Returns:
            None: Modifie l'onglet cible.
        """

        first_cell = table.find("table:table-row/table:table-cell", self.namespaces)
        if first_cell is None:
            return
        paragraph = ET.SubElement(first_cell, self._tag("text", "p"))
        frame = ET.SubElement(paragraph, self._tag("draw", "frame"))
        frame.set(self._attr("draw", "name"), f"Example {sheet_name}")
        frame.set(self._attr("text", "anchor-type"), "cell")
        frame.set(self._attr("svg", "width"), "6cm")
        frame.set(self._attr("svg", "height"), "3cm")
        image = ET.SubElement(frame, self._tag("draw", "image"))
        image.set(self._attr("xlink", "href"), image_path)
        image.set(self._attr("xlink", "type"), "simple")
        image.set(self._attr("xlink", "show"), "embed")
        image.set(self._attr("xlink", "actuate"), "onLoad")

    def _build_manifest(self, content: bytes) -> bytes:
        """Construit le manifeste sans references aux binaires personnels.

        Args:
            content (bytes): Manifeste XML original.

        Returns:
            bytes: Manifeste XML nettoye.
        """

        self._register_namespaces()
        root = ET.fromstring(content)
        for entry in list(root.findall("manifest:file-entry", self.namespaces)):
            if self._is_private_binary_entry(entry.attrib.get(self._attr("manifest", "full-path"), "")):
                root.remove(entry)
        for image_path, _, _ in self.data.platform_images.values():
            entry = ET.SubElement(root, self._tag("manifest", "file-entry"))
            entry.set(self._attr("manifest", "full-path"), image_path)
            entry.set(self._attr("manifest", "media-type"), "image/png")
        return ET.tostring(root, encoding="UTF-8", xml_declaration=True)

    def _add_example_images(self, entries: dict[str, bytes]) -> None:
        """Ajoute les images exemples generees a l'archive.

        Args:
            entries (dict[str, bytes]): Entrees de l'archive en cours.

        Returns:
            None: Ajoute les entrees PNG.
        """

        for image_path, start_color, end_color in self.data.platform_images.values():
            entries[image_path] = self.png_builder.build(start_color, end_color)

    def _register_namespaces(self) -> None:
        """Enregistre les prefixes XML ODS.

        Args:
            Aucun.

        Returns:
            None: Configure ElementTree.
        """

        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)

    def _tag(self, namespace: str, name: str) -> str:
        """Construit un nom XML qualifie.

        Args:
            namespace (str): Cle d'espace de noms.
            name (str): Nom local.

        Returns:
            str: Nom XML qualifie.
        """

        return f"{{{self.namespaces[namespace]}}}{name}"

    def _attr(self, namespace: str, name: str) -> str:
        """Construit un nom d'attribut XML qualifie.

        Args:
            namespace (str): Cle d'espace de noms.
            name (str): Nom local.

        Returns:
            str: Nom d'attribut XML qualifie.
        """

        return self._tag(namespace, name)
