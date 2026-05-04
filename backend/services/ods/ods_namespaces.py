#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import xml.etree.ElementTree as ET


class OdsNamespaces:
    values = {
        "calcext": "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0",
        "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "of": "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
        "oooc": "http://openoffice.org/2004/calc",
        "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "xlink": "http://www.w3.org/1999/xlink",
    }

    @classmethod
    def register(cls) -> None:
        """Declare les espaces de noms ODS aupres du parseur XML.

        Args:
            Aucun.

        Returns:
            None: Les namespaces sont enregistres globalement dans ElementTree.
        """

        for namespace_prefix, namespace_uri in cls.values.items():
            ET.register_namespace(namespace_prefix, namespace_uri)
