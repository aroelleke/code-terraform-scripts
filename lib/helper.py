def clamp(value: number, minumum: number, maximum: number):
    return min(maximum, max(value, minumum))


def clampl(values: List[number], min: number, max: number):
    return [clamp(value, min, max) for value in values]


def average(items: List[Any], key: str = None):
    if not items:
        return 0

    if key:
        items = [i[key] for i in items]
    return sum(items) / len(items)


def calculate_next_step_of_value(value: number, step: number):
    return value - (value % step) + step


def format_money(value: int):
    return f"{value:,}$"


def position_to_coords(position: Position) -> tuple[int, int]:
    return [position.x, position.y]


def coords_to_position(coords: tuple[int, int]) -> VaultPosition:
    return Position(coords[0], coords[1])


def is_point_in_rect(px: int | float, py: int | float, rx: int | float, ry: int | float, w: int | float, h: int | float) -> bool:
    return rx <= px <= rx + w and ry <= py <= ry + h


def is_point_in_circle(px: int | float, py: int | float, cx: int | float, cy: int | float, radius: int | float) -> bool:
    dx = px - cx
    dy = py - cy
    return (dx * dx + dy * dy) <= (radius * radius)


def text_dims(text: str, size: int) -> (float, float):
    w = len(text) * (size / 1.65)
    # h = size
    h = len(text) * size
    return (w, h)


def safe_call_func(obj, name):
    f = getattr(obj, name, None)
    if callable(f):
        return f()


def panel_to_world_coords(
    screen_x: int | float,
    screen_y: int | float,
    center_screen: tuple[int | float, int | float],
    center_world: tuple[int | float, int | float],
    zoom: int | float = 1,
) -> tuple[int, int]:
    dx = (screen_x - center_screen[0]) / zoom
    dy = (screen_y - center_screen[1]) / zoom

    world_x = int(center_world[0] + dx)
    world_y = int(center_world[1] - dy)

    return world_x, world_y


def world_to_panel_coords(
    world_x: int | float,
    world_y: int | float,
    center_screen: tuple[int | float, int | float],
    center_world: tuple[int | float, int | float],
    zoom: int | float = 1,
) -> tuple[int, int]:
    dx = (world_x - center_world[0]) * zoom
    dy = (world_y - center_world[1]) * zoom

    screen_x = int(center_screen[0] + dx)
    screen_y = int(center_screen[1] - dy)

    return screen_x, screen_y


def vehicle_has_module(vehicle: Rover | Pioneer, module_id: str):
    return bool([module.module_id for module in vehicle.modules() if module.module_id == module_id])


def vehicle_has_nav_module(vehicle: Rover | Pioneer):
    return vehicle_has_module(vehicle, "nav_module")


class Position:
    x: number
    y: number

    def __init__(self, x: number, y: number):
        super().__init__(self, x, y)
        self.x = x
        self.y = y
