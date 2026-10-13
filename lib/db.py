from typing import TypeVar, Generic, Any
from type_defs import TaskKey

CKey = TypeVar("CKey", bound=str)
DKey = TypeVar("DKey", bound=str)

DEFAULT_TASKS = {
    "active": None,
    "queue": [],
    "history": [],
}


class Store(Generic[CKey, DKey]):
    def __init__(self, key: str, default_config: dict = None, default_data: dict = None):
        self.key = key
        self.notebook = get_component("notebook")

        # In-Memory Cache
        self._cache: dict[str, dict] = {
            "config": default_config or {},
            "data": default_data or {},
            "task": dict(DEFAULT_TASKS),
        }
        self._dirty: bool = False

    def refresh(self):
        """Holt die Daten unter f'{key}' genau einmal aus dem Notebook (z. B. in prepare())."""
        raw = self.notebook.get(self.key, None)
        if isinstance(raw, dict):
            # Vorhandene Daten einpflegen, fehlende Bereiche durch Defaults absichern
            self._cache["config"] = {**self._cache["config"], **raw.get("config", {})}
            self._cache["data"] = {**self._cache["data"], **raw.get("data", {})}
            self._cache["task"] = {**DEFAULT_TASKS, **raw.get("task", {})}
        else:
            # Erster Start: Defaults im Notebook anlegen
            self.notebook.set(self.key, self._cache)

        self._dirty = False

    def flush(self):
        """Schreibt den Cache zurück, falls Änderungen vorliegen."""
        if self._dirty:
            self.notebook.set(self.key, self._cache)
            self._dirty = False

    # --- Config-Zugriff (typisiert durch CKey) ---

    def config(self, key: CKey, default: Any = None) -> Any:
        return self._cache["config"].get(key, default)

    def set_config(self, key: CKey, value: Any):
        if self._cache["config"].get(key) != value:
            self._cache["config"][key] = value
            self._dirty = True
            # Optional direkt schreiben:
            self.notebook.set(self.key, self._cache)

    # --- Data-Zugriff (typisiert durch DKey) ---

    def data(self, key: DKey, default: Any = None) -> Any:
        return self._cache["data"].get(key, default)

    def set_data(self, key: DKey, value: Any):
        if self._cache["data"].get(key) != value:
            self._cache["data"][key] = value
            self._dirty = True
            self.notebook.set(self.key, self._cache)

    # --- Task-Zugriff (typisiert durch TaskKey) ---

    def task(self, key: TaskKey, default: Any = None) -> Any:
        return self._cache["task"].get(key, default)

    def set_task(self, key: TaskKey, value: Any):
        if self._cache["task"].get(key) != value:
            self._cache["task"][key] = value
            self._dirty = True
            self.notebook.set(self.key, self._cache)
