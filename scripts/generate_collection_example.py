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
# Description : point d'entree de generation du fichier collection-example.ods.
from __future__ import annotations

from pathlib import Path

from collection_example.ods_template_generator import StyledCollectionExampleGenerator


if __name__ == "__main__":
    StyledCollectionExampleGenerator(Path("collection-example.ods")).generate()
