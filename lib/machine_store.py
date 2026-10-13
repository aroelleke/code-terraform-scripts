from dataclasses import fields, is_dataclass
from machine_actions import deserialize_action, Actions
from typing import TypeVar, Generic, Type

C = TypeVar("C")


class MachineStore(Generic[C]):
    def __init__(self, key: str, config_cls: Type[C]):
        self.key = key
        self.notebook = get_component("notebook")
        self._config_cls = config_cls
        self.config: C = config_cls()
        self.job: dict | None = None
        self.refresh()

    def refresh(self):
        # sync state from notebook storage
        raw = self.notebook.get(self.key, {})
        if not isinstance(raw, dict):
            raw = {}

        # load config attributes safely into typed dataclass
        cfg_data = raw.get("config", {})
        for field in fields(self._config_cls):
            if field.name in cfg_data:
                setattr(self.config, field.name, cfg_data[field.name])

        self.job = raw.get("job")

    def save_config(self):
        # serialize flat dataclass fields without heavy reflection or asdict
        raw = self.notebook.get(self.key, {})
        if not isinstance(raw, dict):
            raw = {}

        raw["config"] = {f.name: getattr(self.config, f.name) for f in fields(self._config_cls)}
        self.notebook.set(self.key, raw)

    def get_current_action(self) -> Actions | None:
        if not self.job or not self.job.get("actions"):
            return None
        idx = self.job.get("step_index", 0)
        actions = self.job.get("actions", [])
        if idx >= len(actions):
            return None
        return deserialize_action(actions[idx])

    def assign_job(self, actions: list, routine_name: str = "", loop: bool = True):
        # start a new job routine from the beginning
        raw = self.notebook.get(self.key, {})
        if not isinstance(raw, dict):
            raw = {}

        self.job = {
            "routine_name": routine_name,
            "actions": actions,
            "step_index": 0,
            "loop": loop,
        }
        raw["job"] = self.job
        self.notebook.set(self.key, raw)

    def advance_step(self):
        # progress active job to the next action or restart if looping
        if not self.job:
            return

        actions = self.job.get("actions", [])
        idx = self.job.get("step_index", 0) + 1
        loop = self.job.get("loop", False)

        if idx < len(actions):
            self.job["step_index"] = idx
        else:
            if loop:
                self.job["step_index"] = 0
            else:
                self.job = None

        raw = self.notebook.get(self.key, {})
        if not isinstance(raw, dict):
            raw = {}

        raw["job"] = self.job
        self.notebook.set(self.key, raw)

    def cancel_job(self):
        # abort active job completely
        self.job = None
        raw = self.notebook.get(self.key, {})
        if isinstance(raw, dict):
            raw["job"] = None
            self.notebook.set(self.key, raw)
