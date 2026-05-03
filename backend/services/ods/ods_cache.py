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
from threading import RLock
from typing import Any, Callable


class OdsCache:
    _entries: dict[str, dict[str, Any]] = {}
    _lock = RLock()

    def __init__(self, ods_path: str):
        """Initialise le cache associe a un fichier ODS.

        Args:
            ods_path (str): Chemin du fichier ODS utilise comme cle de cache.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.ods_path = os.path.abspath(ods_path)

    def remember(self, key: str, factory: Callable[[], Any]) -> Any:
        """Retourne une valeur en cache ou la construit a la premiere demande.

        Args:
            key (str): Cle logique de la donnee mise en cache.
            factory (Callable[[], Any]): Fonction appelee uniquement si la cle est absente.

        Returns:
            Any: Copie de la valeur cachee ou nouvellement construite.
        """

        with self._lock:
            file_cache = self._entries.setdefault(self.ods_path, {})
            if key not in file_cache:
                file_cache[key] = factory()
            return self._clone(file_cache[key])

    def reset(self) -> int:
        """Vide toutes les donnees en cache du fichier ODS courant.

        Args:
            Aucun.

        Returns:
            int: Nombre d'entrees supprimees du cache.
        """

        with self._lock:
            removed_entries = len(self._entries.get(self.ods_path, {}))
            self._entries.pop(self.ods_path, None)
            return removed_entries

    def _clone(self, value: Any) -> Any:
        """Copie une valeur pour proteger le cache des mutations externes.

        Args:
            value (Any): Valeur stockee dans le cache.

        Returns:
            Any: Copie independante quand le type le permet.
        """

        if value.__class__.__module__.startswith("pandas.") and hasattr(value, "copy"):
            try:
                return value.copy(deep=True)
            except TypeError:
                return value.copy()
        return copy.deepcopy(value)
