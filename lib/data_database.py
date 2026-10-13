from machine_store import Database


class Data(Database):
    def __init__(self, key: str, defaults: JsonValue = None):
        key = f"{key}.data"
        super().__init__(key, defaults)
