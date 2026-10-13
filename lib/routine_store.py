class RoutineStore:
    def __init__(self, category: str):
        self.key = f"routines.{category}"
        self.notebook = get_component("notebook")

    def all(self) -> dict:
        data = self.notebook.get(self.key, {})
        return data if isinstance(data, dict) else {}

    def get(self, name: str) -> dict | None:
        return self.all().get(name)

    def save(self, name: str, actions: list, loop: bool = False):
        routines = self.all()
        routines[name] = actions
        self.notebook.set(self.key, routines)

    def delete(self, name: str):
        routines = self.all()
        if name in routines:
            del routines[name]
            self.notebook.set(self.key, routines)
