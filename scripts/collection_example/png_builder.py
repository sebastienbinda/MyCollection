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
# Description : utilitaire objet de creation d'images PNG factices.
from __future__ import annotations

import binascii
import struct
from zlib import compress


class ExamplePngBuilder:
    """Genere des images PNG neutres sans fichier source externe."""

    def build(self, start_color: tuple[int, int, int], end_color: tuple[int, int, int]) -> bytes:
        """Genere une image PNG en degrade.

        Args:
            start_color (tuple[int, int, int]): Couleur RGB de depart.
            end_color (tuple[int, int, int]): Couleur RGB d'arrivee.

        Returns:
            bytes: Image PNG generee.
        """

        width, height = 320, 160
        rows = [self._build_row(y, width, height, start_color, end_color) for y in range(height)]
        return (
            b"\x89PNG\r\n\x1a\n"
            + self._chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + self._chunk(b"IDAT", compress(b"".join(rows)))
            + self._chunk(b"IEND", b"")
        )

    def _build_row(
        self,
        y: int,
        width: int,
        height: int,
        start_color: tuple[int, int, int],
        end_color: tuple[int, int, int],
    ) -> bytes:
        """Construit une ligne de pixels PNG.

        Args:
            y (int): Index vertical de la ligne.
            width (int): Largeur de l'image.
            height (int): Hauteur de l'image.
            start_color (tuple[int, int, int]): Couleur RGB de depart.
            end_color (tuple[int, int, int]): Couleur RGB d'arrivee.

        Returns:
            bytes: Ligne encodee avec le filtre PNG.
        """

        row = bytearray([0])
        for x in range(width):
            ratio = (x + y) / (width + height - 2)
            row.extend(self._interpolate(start_color, end_color, ratio))
        return bytes(row)

    def _interpolate(
        self,
        start_color: tuple[int, int, int],
        end_color: tuple[int, int, int],
        ratio: float,
    ) -> bytes:
        """Calcule une couleur intermediaire RGB.

        Args:
            start_color (tuple[int, int, int]): Couleur RGB initiale.
            end_color (tuple[int, int, int]): Couleur RGB finale.
            ratio (float): Position entre 0 et 1 dans le degrade.

        Returns:
            bytes: Trois octets RGB.
        """

        return bytes(round(start + (end - start) * ratio) for start, end in zip(start_color, end_color))

    def _chunk(self, chunk_type: bytes, data: bytes) -> bytes:
        """Construit un bloc PNG valide.

        Args:
            chunk_type (bytes): Type du bloc PNG sur quatre octets.
            data (bytes): Donnees binaires du bloc.

        Returns:
            bytes: Bloc PNG encode avec taille et CRC.
        """

        crc = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)
