from layout_cursor import LayoutCursor
import math


class PanelWrapper:
    def __init__(self, panel: Panel, key: str):
        self.panel: Panel = panel
        self.key = f"panel.{key}"

        self.c: LayoutCursor

        self.root: bool = False
        self.click_list: list[PanelClick] = []
        self.mouse: PanelMouse | None = None

    def prepare(self, x: int = 0, y: int = 0, mouse: PanelMouse = None, click_list: list[PanelClick] = [], **_):
        self.c = LayoutCursor(x, y)

        self.click_list = click_list
        self.mouse = mouse

    def draw_button(
        self, label: str, click_fn: Callable, payload=None, active: bool = False, disabled: bool = False, options: DrawButtonOptions = {}
    ):
        # self.c.save()
        # Fill options with defaults
        options = {**DEFAULT_DRAW_BUTTON_OPTIONS, **options}

        # Auto adjust width to label length
        if options["w"] == "auto":
            options["w"] = 14 + (len(label) * (options["text-size"] / 1.65))

        # Hover listener
        hover: bool = False
        m = self.panel.mouse()
        if m.over and m.x > self.c.x and m.x < self.c.x + options["w"] and m.y > self.c.y and m.y < self.c.y + options["h"]:
            hover = True

        # Set state to dynamically use themes
        state = "-disabled" if disabled else "-active" if active else "-hover" if hover else ""

        # Background
        self.panel.fill_rect(self.c.x, self.c.y, options["w"], options["h"], options[f"bg-color{state}"])

        # Border
        # if not disabled:
        #     self.panel.fill_rect(
        #         self.c.x + options["w"] - (options["w"] * 0.2), self.c.y + options["h"] - 1, options["w"] * 0.2, 1, options[f"border-color{state}"]
        #     )
        self.panel.fill_rect(self.c.x, self.c.y, 4 if active or disabled else 2, options["h"], options[f"border-color{state}"])

        # Text
        self.panel.draw_text(self.c.x + 8, self.c.y + (options["h"] / 2), label, options["text-size"], options[f"text-color{state}"])

        # Click listener
        if not disabled:
            for c in self.click_list:
                if c.x > self.c.x and c.x < self.c.x + options["w"] and c.y > self.c.y and c.y < self.c.y + options["h"]:
                    click_fn(*[payload if payload else label])

        return options["w"]

    def draw_switch(self, label: str, key: str, active: bool, options: DrawOptions = {}):
        self.c.save()

        options = {**DEFAULT_DRAW_SWITCH_OPTIONS, **options}
        if options["size"] == "auto":
            options["size"] = options["h"] * 0.55

        self.panel.fill_rect(self.c.x, self.c.y, options["w"], options["h"], options["bg-color-active"] if active else options["bg-color"])

        self.panel.fill_rect(
            self.c.x + options["w"] - 30, self.c.y + options["h"] - 1, 30, 1, options["border-color-active"] if active else options["border-color"]
        )
        self.panel.fill_rect(self.c.x, self.c.y, 2, options["h"], options["border-color-active"] if active else options["border-color"])

        self.c.x += 8

        if options["refresh"]:
            self.panel.forget(key)
        state = self.panel.switch(key, self.c.x, self.c.y + (options["size"] * 0.4), active, size=options["size"])

        self.c.x += (options["size"] * 2) + 5
        self.panel.draw_text(self.c.x, self.c.y + 10, label, options["text_size"], options["text-color-active"] if active else options["text-color"])

        self.c.load()
        return state

    def fill_regular_polygon(
        self,
        cx: int | float,
        cy: int | float,
        radius: int | float,
        sides: int,
        color: str,
        angle: float = 0.0,
    ):
        if sides < 3:
            return

        # -90° to make sure the polygon is topsided
        start_angle_rad = math.radians(-90 + angle)
        step_rad = (2 * math.pi) / sides

        points: list[int] = []
        for i in range(sides):
            current_angle = start_angle_rad + (i * step_rad)
            px = cx + radius * math.cos(current_angle)
            py = cy + radius * math.sin(current_angle)
            points.extend([int(round(px)), int(round(py))])

        self.panel.fill_polygon(points, color)

    def draw_regular_polygon(
        self,
        cx: int | float,
        cy: int | float,
        radius: int | float,
        sides: int,
        color: str,
        width: float = 1,
        angle: float = 0.0,
    ):
        if sides < 3:
            return

        # -90° to make sure the polygon is topsided
        start_angle_rad = math.radians(-90 + angle)
        step_rad = (2 * math.pi) / sides

        points: list[tuple[int, int]] = []
        for i in range(sides):
            current_angle = start_angle_rad + (i * step_rad)
            px = cx + radius * math.cos(current_angle)
            py = cy + radius * math.sin(current_angle)
            points.extend([int(round(px)), int(round(py))])

        self.panel.draw_polygon(points, color, width)

    def fill_star(
        self,
        cx: int | float,
        cy: int | float,
        radius_1: int | float,
        radius_2: int | float,
        sides: int,
        color: str,
        angle: float = 0.0,
    ):
        if sides < 3:
            return

        r_outer = max(radius_1, radius_2)
        r_inner = min(radius_1, radius_2)

        start_angle_rad = math.radians(-90 + angle)
        step_rad = math.pi / sides

        points: list[int] = []
        for i in range(sides * 2):
            current_angle = start_angle_rad + (i * step_rad)
            r = r_outer if i % 2 == 0 else r_inner

            px = cx + r * math.cos(current_angle)
            py = cy + r * math.sin(current_angle)
            points.extend([int(round(px)), int(round(py))])

        self.panel.fill_polygon(points, color)

    def draw_star(
        self,
        cx: int | float,
        cy: int | float,
        radius_1: int | float,
        radius_2: int | float,
        sides: int,
        color: str,
        width: float = 1,
        angle: float = 0.0,
    ):
        if sides < 3:
            return

        r_outer = max(radius_1, radius_2)
        r_inner = min(radius_1, radius_2)

        start_angle_rad = math.radians(-90 + angle)
        step_rad = math.pi / sides

        points: list[int] = []
        for i in range(sides * 2):
            current_angle = start_angle_rad + (i * step_rad)
            r = r_outer if i % 2 == 0 else r_inner

            px = cx + r * math.cos(current_angle)
            py = cy + r * math.sin(current_angle)
            points.extend([int(round(px)), int(round(py))])

        self.panel.draw_polygon(points, color, width)


DrawOptions = {
    "w": (int, "auto"),
    "h": int,
    "text_size": int,
    "text_color": str,
    "text_color-hover": str,
    "text_color-active": str,
    "text_color-disabled": str,
    "size": (int, "auto"),
    "refresh": bool,
    "bg-color": str,
    "bg-color-hover": str,
    "bg-color-active": str,
    "bg-color-disabled": str,
    "border-color": str,
    "border-color-hover": str,
    "border-color-active": str,
    "border-color-disabled": str,
}

DEFAULT_DRAW_BUTTON_OPTIONS: DrawOptions = {
    "w": "auto",
    "h": 20,
    "text-size": 11,
    "text-color": "accent",
    "text-color-hover": "accent",
    "text-color-active": "white",
    "text-color-disabled": "#868290",
    "bg-color": "#2a2238",
    "bg-color-hover": "#3b3050",
    "bg-color-active": "#2a2238",
    "bg-color-disabled": "#3b3842",
    "border-color": "accent",
    "border-color-hover": "accent",
    "border-color-active": "accent",
    "border-color-disabled": "#868290",
}

DEFAULT_DRAW_SWITCH_OPTIONS: DrawOptions = {
    "h": 20,
    "size": "auto",
    "text-color": "warning",
    "text-color-active": "success",
    "text_size": 11,
    "refresh": False,
    "bg-color": "#1e1f27",
    "bg-color-active": "#1e1f27",
    "border-color": "error",
    "border-color-active": "success",
}
