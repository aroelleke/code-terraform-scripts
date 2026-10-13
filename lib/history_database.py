from machine_store import Database


DEFAULT_DATA = {
    "task": None,
    "queue": None,
    "history": None,
}


class Task(Database):
    def __init__(self, key: str, tasks: dict):
        key = f"{key}.task"
        super().__init__(key, [])

    def history(self, start: int = 0, end: int = -1) -> list[dict] | None:
        history: JsonValue = self.get("history")
        if isinstance(history, list):
            return list(history)[start:end]

    def history_add(self, task):
        history = self.history()
        history.insert(0, task)
        self.notebook.set(self.key, history)

    def history_remove(self, index: int = -1):
        history = self.history()
        if history:
            history.pop(index)
            self.set_all()

    def history_clear(self):
        self.set_all(self.DEFAULTS)


# class TaskTest:
#     def __init__(self, key: str):
#         match key:
#             case "vehicle":
#                 self.set_vehicle_props()
#         self.action: str = ""
#         self.action: str = ""

#     def set_vehicle_props(self):
#         self.m


# TASK_TYPES = {
#     "vehicle": {
#         "actions": {
#             "mount_module": ["module_index"],
#             "unmount_module": ["module_index", "item_id"],
#             "install",
#             "uninstall",
#             "charge",
#             "move"},
#     }
# }
