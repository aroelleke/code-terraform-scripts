from dataclasses import dataclass, asdict, field
from typing import TypeVar, Generic, Type, Any


@dataclass
class TaskItem:
    # generic base task that machine-specific tasks inherit from
    action: str
    id: str | None = None
    status: str = "pending"  # pending, running, completed, cancelled, failed


T = TypeVar("T", bound=TaskItem)


class TaskManager(Generic[T]):
    def __init__(self, task_class: Type[T], max_history: int = 20):
        self._task_class = task_class
        self.max_history = max_history
        self.active: T | None = None
        self.queue: list[T] = []
        self.history: list[dict] = []

    def load(self, data: dict):
        # hydrate task models from notebook data
        active_raw = data.get("active")
        self.active = self._deserialize(active_raw) if active_raw else None

        queue_raw = data.get("queue", [])
        self.queue = [self._deserialize(item) for item in queue_raw if item]

        self.history = data.get("history", [])

    def to_dict(self) -> dict:
        # pack everything back into a clean dict for notebook storage
        return {
            "active": asdict(self.active) if self.active else None,
            "queue": [asdict(t) for t in self.queue],
            "history": self.history[-self.max_history :],
        }

    def _deserialize(self, item_data: dict) -> T:
        # filter out stray properties so dataclass instantiation won't break
        valid_fields = {k: v for k, v in item_data.items() if k in self._task_class.__dataclass_fields__}
        return self._task_class(**valid_fields)

    def add(self, task: T, start_immediately: bool = True):
        # enqueue a task and kick it off right away if the queue is currently idle
        self.queue.append(task)
        if start_immediately and self.active is None:
            self.next()

    def next(self) -> T | None:
        # pop the next pending task from the front of the queue
        if self.queue:
            self.active = self.queue.pop(0)
            self.active.status = "running"
        else:
            self.active = None
        return self.active

    def complete_active(self, result_msg: str = "success") -> T | None:
        # finish up current job, log it to history, and pull the next one
        if self.active:
            self.active.status = "completed"
            entry = asdict(self.active)
            entry["result"] = result_msg
            self._archive(entry)
            return self.next()
        return None

    def cancel_active(self, reason: str = "cancelled") -> T | None:
        # bail out of current task without wiping remaining queue
        if not self.active:
            return

        self.active.status = "cancelled"
        entry = asdict(self.active)
        entry["reason"] = reason
        self._archive(entry)
        self.active = None

    def clear_queue(self):
        self.queue.clear()

    def _archive(self, entry: dict):
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)
