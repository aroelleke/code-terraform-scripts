from dataclasses import dataclass, field
from machine_actions import TargetSetAction, FollowAction, Actions
from machine_store import MachineStore
from page_panel import PagePanel
import helper as Helper


LOCATION_THEME: dict[str, dict[str, str]] = {
    "unknown": {"color": "#5d5d5d", "text": "?", "text_color": "white"},
    "mineral": {"color": "#dfe168", "text": "M", "text_color": "black"},
    "biomass": {"color": "#109906", "text": "B", "text_color": "white"},
    "thermal": {"color": "#8e4602", "text": "T", "text_color": "white"},
    "water": {"color": "#063698", "text": "W", "text_color": "white"},
    "oil": {"color": "#000000", "text": "O", "text_color": "white"},
    "exotic": {"color": "#8f0062", "text": "E", "text_color": "white"},
    "inert": {"color": "#898989", "text": "I", "text_color": "black"},
}

VEHICLE_THEME: dict[str, str] = {
    "rover": "#31c83e",
    "pioneer": "#5231c8",
}


@dataclass
class BiomeColors:
    frozen: str = "#18293d"
    coastal: str = "#284016"
    geothermal: str = "#3b2f14"
    volcanic: str = "#471a15"
    deep: str = "#353c45"


@dataclass
class MapConfig:
    enabled: bool = True
    auto_charge: bool = True
    throttle: float = 0.5
    zoom_base: int = 13
    zoom_level: int = 0
    zoom_level_max: int = 4
    biomes: bool = True
    outposts: bool = True
    locations: bool = True
    vehicles: bool = True
    drones: bool = True
    biome_colors: BiomeColors = field(default_factory=BiomeColors)


class MapPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, key="map", root=True)

        self.store: MachineStore[MapConfig] = MachineStore("panel.map", MapConfig)

        self.fleet: Fleet = get_component("fleet")
        self.outpost_network: OutpostNetwork = get_component("outpost_network")
        self.power_control: PowerControl = get_component("power_control")
        self.planet: Nocturna = get_component("nocturna")

        self.w: int = 0
        self.h: int = 0
        self.map_coords: tuple[int, int] = (0, 0)

        self.outpost_list: list[OutpostRef] = []
        self.location_list: list[PointOfInterest] = []
        self.vehicle_list: list[VehicleRef] = []
        self.drone_list: list[DroneRef] = []
        self.grid_list: list[PowerGrid] = []

        self.last_rendered_coords: tuple[int, int] | None = None

        self.action: Action = self.store.get_current_action()
        self.target_coords: tuple[int, int] = (0, 0)
        self.active_map_point: dict | None = None

        # Shape Renderer Mapping
        self.shape_renderers = {
            "rectangle": self._draw_shape_rectangle,
            "circle": self._draw_shape_circle,
            "triangle": self._draw_shape_triangle,
            "gem": self._draw_shape_gem,
            "star": self._draw_shape_star,
        }

    def prepare(self, **_):
        super().prepare(**_)
        self.store.refresh()

        self.outpost_list = self.outpost_network.outposts()
        self.vehicle_list = self.fleet.vehicles()
        self.grid_list = self.power_control.grids()
        self.location_list = self.planet.points_of_interest()
        self.drone_list = self.fleet.drones()

        self.w = self.panel.width() - (self.c.x * 2)
        self.h = self.panel.height() - (self.c.y * 2) - 30
        self.map_coords = (self.c.x, self.c.y + 25)

        self.set_map_center()

    def set_map_center(self):
        target_coords: tuple[int, int] = (0, 0)

        match self.action:
            case TargetSetAction(coords):
                target_coords = coords
            case FollowAction(type, target_id):
                ref = get_component(target_id)
                if ref:
                    match type:
                        case "outpost":
                            target_coords = ref.coords()
                        case "vehicle":
                            if Helper.vehicle_has_nav_module(ref):
                                target_coords = Helper.position_to_coords(ref.nav.get_position())
                        case "drone":
                            target_coords = Helper.position_to_coords(ref.position())

        map_size = self.planet.get_bounds()
        if not (map_size.min_x <= target_coords[0] <= map_size.max_x and map_size.min_y <= target_coords[1] <= map_size.max_y):
            target_coords = (0, 0)

        self.target_coords = []
        for n in target_coords:
            self.target_coords.append(int(n))

    def render(self, **_):
        super().render(**_)

        if self.panel.icon_button("map.config", self.c.x, self.c.y, 20, "console"):
            self.show_config = not self.show_config

        self.draw_header()
        self.c.y += 25

        if self.store.config.enabled:
            self.draw_map()

        self.draw_border()

        if self.show_config:
            self.draw_config()

    def draw_header(self):
        self.draw_enable_switch()

        self.draw_center_coords()
        if self.action and self.action.action == "follow":
            self.draw_following()

        self.draw_mouse_coords()
        self.draw_zoom_selection()

    def draw_center_coords(self):
        self.c.save()
        self.c.x += 30

        self.panel.draw_text(self.c.x, self.c.y + 3, "CENTER", 6, "text-muted")
        self.panel.draw_text(self.c.x + 0.4, self.c.y + 3, "CENTER", 6, "text-muted")
        self.panel.fill_rect(self.c.x, self.c.y + 6, len("CENTER") * (6 / 1.65) + 0.3, 1, "text-muted")

        self.c.x += 25
        self.c.y += 15

        coords_x = str(self.target_coords[0]) if self.store.config.enabled else "-"
        coords_y = str(self.target_coords[1]) if self.store.config.enabled else "-"

        self.panel.draw_text(self.c.x - (len(coords_x) * (10 / 1.65)), self.c.y, coords_x, 10, "white" if self.store.config.enabled else "error")
        self.c.x += 1
        self.panel.draw_text(self.c.x, self.c.y, "|", 10, "text-muted")
        self.c.x += 9
        self.panel.draw_text(self.c.x, self.c.y, coords_y, 10, "white" if self.store.config.enabled else "error")
        self.c.load()

    def draw_following(self):
        self.c.save()
        self.c.x += 105

        self.panel.draw_text(self.c.x, self.c.y + 3, "FOLLOWING", 6, "text-muted")
        self.panel.draw_text(self.c.x + 0.4, self.c.y + 3, "FOLLOWING", 6, "text-muted")
        self.panel.fill_rect(self.c.x, self.c.y + 6, len("FOLLOWING") * (6 / 1.65) + 0.3, 1, "text-muted")

        self.c.y += 15

        self.panel.draw_text(self.c.x, self.c.y, self.action.target_id, 10, "white" if self.store.config.enabled else "error")
        self.c.load()

    def draw_mouse_coords(self):
        self.c.save()
        self.c.x += self.w - 240

        self.panel.draw_text(self.c.x, self.c.y + 3, "MOUSE", 6, "text-muted")
        self.panel.draw_text(self.c.x + 0.4, self.c.y + 3, "MOUSE", 6, "text-muted")
        self.panel.fill_rect(self.c.x, self.c.y + 6, len("MOUSE") * (6 / 1.65) + 0.3, 1, "text-muted")

        self.c.x += 25
        self.c.y += 15

        m = self.panel.mouse()
        active = m.over and self.store.config.enabled and Helper.is_point_in_rect(m.x, m.y, self.map_coords[0], self.map_coords[1], self.w, self.h)

        center_screen = (self.map_coords[0] + (self.w / 2), self.map_coords[1] + (self.h / 2))

        mouse_world_x, mouse_world_y = Helper.panel_to_world_coords(
            m.x, m.y, center_screen, self.target_coords, zoom=self.store.config.zoom_base**self.store.config.zoom_level
        )

        coords_x = str(mouse_world_x) if active else "-"
        coords_y = str(mouse_world_y) if active else "-"

        self.panel.draw_text(self.c.x - (len(coords_x) * (10 / 1.65)), self.c.y, coords_x, 10, "white" if self.store.config.enabled else "error")
        self.c.x += 1
        self.panel.draw_text(self.c.x, self.c.y, "|", 10, "text-muted")
        self.c.x += 9
        self.panel.draw_text(self.c.x, self.c.y, coords_y, 10, "white" if self.store.config.enabled else "error")
        self.c.load()

    def draw_zoom_selection(self):
        self.c.save()
        self.c.x += self.w - 170

        zoom_level = self.store.config.zoom_level
        zoom_level_max = self.store.config.zoom_level_max

        self.panel.draw_text(self.c.x, self.c.y + 3, "ZOOM-LEVEL", 6, "text-muted")
        self.panel.draw_text(self.c.x + 0.4, self.c.y + 3, "ZOOM-LEVEL", 6, "text-muted")
        self.panel.fill_rect(self.c.x, self.c.y + 6, len("ZOOM-LEVEL") * (6 / 1.65) + 0.3, 1, "text-muted")

        self.c.x += 55
        self.panel.draw_text(self.c.x - (len(str(zoom_level)) * (13 / 1.65)), self.c.y + 10, str(zoom_level), 13, "white")
        self.c.x += 5

        self.draw_increase_number_button("+", click_fn=self.higher_zoom, disabled=zoom_level >= zoom_level_max)
        self.draw_increase_number_button("-", click_fn=self.lower_zoom, disabled=zoom_level <= -zoom_level_max)

        self.c.load()

    def lower_zoom(self, _):
        self.store.config.zoom_level = self.store.config.zoom_level - 1
        self.store.save_config()

    def higher_zoom(self, _):
        self.store.config.zoom_level = self.store.config.zoom_level + 1
        self.store.save_config()

    def draw_enable_switch(self):
        self.c.save()
        self.c.y += 3
        self.c.x += self.w - 80

        switch_state = self.panel.switch("map.enable", self.c.x, self.c.y, self.store.config.enabled, size=15)
        self.c.x += 34
        self.panel.draw_text(self.c.x, self.c.y + 4, "Enabled", 9, "success" if switch_state else "bg-surface")
        self.panel.draw_text(self.c.x, self.c.y + 12, "Disabled", 9, "error" if not switch_state else "bg-surface")

        if switch_state != self.store.config.enabled:
            self.store.config.enabled = not self.store.config.enabled
            self.store.save_config()

        self.c.load()

    def draw_map(self):
        center = (self.c.x + (self.w / 2), self.c.y + (self.h / 2))

        # TODO: enable after fixing usage of biome colors from config
        # if self.store.config.biomes:
        #     self.draw_map_biomes(center)

        self.draw_map_points(center)

    def draw_map_biomes(self, center: tuple[int, int]):
        texture_map = {}
        step_size = 25

        for i in range(self.w // step_size):
            for j in range(self.h // step_size):
                if j not in texture_map:
                    texture_map[j] = ""

                biome_char = self.planet.biome_at(i - self.target_coords[0], j - self.target_coords[1])[:1]
                texture_map[j] = texture_map[j][:i] + biome_char

        if not self.last_rendered_coords or self.last_rendered_coords != self.target_coords:
            self.panel.texture("map_biome_bg", texture_map.values(), self.store.config.biome_colors)
            self.last_rendered_coords = self.target_coords

        self.panel.draw_texture("map_biome_bg", self.c.x, self.c.y, self.w, self.h)

    def draw_map_points(self, center: tuple[int, int]):
        map_points = self.get_map_points()

        rendered_items = []
        for item in map_points:
            screen_x, screen_y = Helper.world_to_panel_coords(
                item["coords"][0], item["coords"][1], center, self.target_coords, zoom=self.store.config.zoom_base**self.store.config.zoom_level
            )

            if abs(screen_x - center[0]) < (self.w / 2) - 10 and abs(screen_y - center[1]) < (self.h / 2) - 10:
                rendered_items.append(((screen_x, screen_y), item))

        # Zentrales Klick-Handling
        if self.click_list:
            clicked_any_item = False
            for c in self.click_list:
                if not Helper.is_point_in_rect(c.x, c.y, self.map_coords[0], self.map_coords[1], self.w, self.h):
                    continue

                for point_coords, item in rendered_items:
                    radius = 8 * (self.store.config.zoom_base**self.store.config.zoom_level)
                    if Helper.is_point_in_circle(c.x, c.y, point_coords[0], point_coords[1], radius + 5):
                        self.active_map_point = item
                        clicked_any_item = True
                        break

                if not clicked_any_item:
                    self.active_map_point = None

        for point_coords, item in rendered_items:
            self.draw_map_point(point_coords, item)

    def draw_map_point(self, point_coords: tuple[int, int], item: dict):
        style = self._get_item_style(item)
        active, hover, radius = self._evaluate_interaction(point_coords, item, style["radius"])

        renderer = self.shape_renderers.get(style["shape"])
        if renderer:
            renderer(point_coords, radius, style["color"], active, hover, item)

        if style.get("text"):
            dims = Helper.text_dims(style["text"], style["text_size"])
            self.panel.draw_text(
                point_coords[0] - dims[0] / 2,
                point_coords[1] + (dims[1] / 2) - dims[1] / 2,
                style["text"],
                style["text_size"],
                style["text_color"],
            )

    def _get_item_style(self, item: dict) -> dict:
        radius = 8 * (self.store.config.zoom_base**self.store.config.zoom_level)
        text_size = 9 * (self.store.config.zoom_base**self.store.config.zoom_level)

        style = {
            "radius": radius,
            "text_size": text_size,
            "shape": "circle",
            "color": "white",
            "text": "",
            "text_color": "black",
        }

        match item["type"]:
            case "outpost":
                style["shape"] = "rectangle"
                style["color"] = "#466f8b"
            case "location":
                style["shape"] = "circle"
                theme = LOCATION_THEME.get(item["kind"], {"color": "#898989", "text": item["kind"][0].capitalize(), "text_color": "black"})
                style["color"] = theme["color"]
                style["text"] = theme["text"]
                style["text_color"] = theme["text_color"]
            case "vehicle":
                style["shape"] = "gem"
                style["text"] = item["kind"][0].capitalize()
                style["color"] = VEHICLE_THEME.get(item["kind"], "#31c83e")
            case "drone":
                style["shape"] = "triangle"
                style["color"] = "#c83184"

        return style

    def _evaluate_interaction(self, point_coords: tuple[int, int], item: dict, base_radius: float) -> tuple[bool, bool, float]:
        active = self.active_map_point == item
        hover = False

        if not active:
            m = self.panel.mouse()
            if Helper.is_point_in_circle(m.x, m.y, point_coords[0], point_coords[1], base_radius + 5):
                hover = True

        radius = base_radius
        if active or hover:
            radius = base_radius + 2 + (base_radius * 0.2)

        return active, hover, radius

    # --- Shape Renderer ---

    def _draw_shape_rectangle(self, point_coords: tuple[int, int], radius: float, color: str, active: bool, hover: bool, item: dict):
        size = radius * 2.5
        rx = point_coords[0] - (size / 2)
        ry = point_coords[1] - (size / 2)

        if active or hover:
            border_offset = 6
            border_color = color if active else "white"
            self.panel.draw_rect(rx - border_offset / 2, ry - border_offset / 2, size + border_offset, size + border_offset, border_color)

        if item.get("is_home"):
            tsize = radius
            self.panel.fill_rect(point_coords[0] - tsize / 2, point_coords[1] - tsize / 2, tsize, tsize, "#178ab0")

        self.panel.fill_rect(rx, ry, size, size, color)

        corner_size = (size - radius) / 2
        if item.get("has_bio"):
            self.panel.fill_rect(rx, ry, corner_size, corner_size, "#1bc101")
        if item.get("has_charging_station"):
            self.panel.fill_rect(rx + size - corner_size, ry, corner_size, corner_size, "#c1aa01")

    def _draw_shape_circle(self, point_coords: tuple[int, int], radius: float, color: str, active: bool, hover: bool, item: dict):
        if active or hover:
            outline_color = color if active else "white"
            self.panel.draw_circle(point_coords[0], point_coords[1], radius + 2, outline_color, 1)
        self.panel.fill_circle(point_coords[0], point_coords[1], radius, color)

    def _draw_shape_triangle(self, point_coords: tuple[int, int], radius: float, color: str, active: bool, hover: bool, item: dict):
        sides = 3
        scaled_radius = radius * 1.3
        if active or hover:
            border_size = scaled_radius * (1.55 if active else 1.1)
            border_color = color if active else "white"
            self.draw_regular_polygon(point_coords[0], point_coords[1], border_size, sides, border_color, border_size * 0.1)
        self.fill_regular_polygon(point_coords[0], point_coords[1], scaled_radius, sides, color)

    def _draw_shape_gem(self, point_coords: tuple[int, int], radius: float, color: str, active: bool, hover: bool, item: dict):
        sides = 4
        scaled_radius = radius * 1.2
        if active or hover:
            border_size = scaled_radius * 1.55 if active else scaled_radius + 3
            border_color = color if active else "white"
            self.draw_regular_polygon(point_coords[0], point_coords[1], border_size, sides, border_color, border_size * 0.1, 45)
        self.fill_regular_polygon(point_coords[0], point_coords[1], scaled_radius, sides, color, 45)

    def _draw_shape_star(self, point_coords: tuple[int, int], radius: float, color: str, active: bool, hover: bool, item: dict):
        sides = 8
        r1, r2 = radius * 0.7, radius * 1.3
        if active or hover:
            border_color = color if active else "white"
            self.draw_star(point_coords[0], point_coords[1], r1 + 3, r2 + 5, sides, border_color, (r1 + 3) * 0.1)
        self.fill_star(point_coords[0], point_coords[1], r1, r2, sides, color)

    # --- Daten-Mappers ---

    def get_map_points(self) -> list[dict]:
        points = []
        if self.store.config.outposts:
            points.extend([self._map_outpost(o) for o in self.outpost_list])
        if self.store.config.locations:
            points.extend([self._map_location(l) for l in self.location_list])
        if self.store.config.vehicles:
            points.extend([self._map_vehicle(v) for v in self.vehicle_list])
        if self.store.config.drones:
            points.extend([self._map_drone(d) for d in self.drone_list])
        return points

    def _map_outpost(self, item: OutpostRef) -> dict:
        return {
            "type": "outpost",
            "id": item.id,
            "name": item.name,
            "coords": item.coords(),
            "is_home": item.is_home,
            "biome": item.biome,
            "has_bio": bool(item.buildings("bio_collector") and item.buildings("bio_lab") and item.buildings("bio_exchange")),
            "has_charging_station": bool(item.buildings("charging_station")),
        }

    def _map_location(self, item: PointOfInterest) -> dict:
        return {
            "type": "location",
            "scanned": item.scanned,
            "kind": item.kind,
            "coords": (item.x, item.y),
        }

    def _map_vehicle(self, item: VehicleRef) -> dict:
        return {
            "type": "vehicle",
            "id": item.id,
            "name": item.name,
            "kind": item.kind,
            "status": item.status,
            "coords": (item.x, item.y),
            "battery_level": item.battery_level,
        }

    def _map_drone(self, item: DroneRef) -> dict:
        return {
            "type": "drone",
            "id": item.id,
            "name": item.name,
            "status": item.status,
            "coords": (item.x, item.y),
            "kind": item.kind,
            "battery_level": item.battery_level,
            "oil_level": item.oil_level,
            "engine": item.engine,
        }

    def draw_border(self):
        self.panel.draw_rect(self.c.x, self.c.y, self.w, self.h, "accent")

    def draw_config(self):
        self.c.save(True)
        self.panel.card(self.c.x, self.c.y, 140, self.h, "MAP CONFIG")

        self.c.x += 10
        self.c.y += 35

        for setting in ["biomes", "outposts", "locations", "vehicles", "drones"]:
            self.draw_switch_config(setting)
            self.c.y += 25

        # TODO: Apply theme and add theme page where theese biome colors may be changed
        # self.panel.divider(self.c.x, self.c.y, self.c.x + 120, self.c.y)
        # self.c.y += 15
        # self.panel.draw_text(self.c.x, self.c.y, "Biome Colors", 11, "white")

        # for biome in ["frozen", "coastal", "geothermal", "volcanic", "deep"]:
        #     self.c.y += 20
        #     self.draw_biome_color_config(biome)

        self.c.load()

    def draw_switch_config(self, setting: str):
        key = f"config.map.{setting}"
        value = bool(getattr(self.store.config, setting))

        state = self.draw_switch(setting.capitalize(), key, value, {"w": 120})
        if state != value:
            setattr(self.store.config, setting, not value)
            self.store.save_config()

    def draw_biome_color_config(self, biome: str):
        self.c.save()
        color = getattr(self.store.config.biome_colors, biome)
        element_key = f"map_config_biome_color.{biome}"

        self.panel.fill_rect(self.c.x - 5, self.c.y - 10, 125, 19, color)
        self.panel.fill_rect(self.c.x - 5, self.c.y - 10, 125, 19, "#00000080")
        self.panel.draw_rect(self.c.x - 5, self.c.y - 10, 125, 19, color)
        self.panel.draw_text(self.c.x, self.c.y, biome.capitalize(), 10, "white")

        self.panel.forget(element_key)
        self.c.x += 62
        new_color = self.panel.text_field(element_key, self.c.x, self.c.y - 10, 58, color, size=19)

        if new_color != color:
            setattr(self.store.config.biome_colors, biome, new_color)
            self.store.save_config()
        self.c.load()

    def draw_increase_number_button(self, label: str, click_fn: Callable, disabled: bool = False):
        w, h = 20, 10
        x, y = self.c.x, self.c.y

        if label == "+":
            y += -1.5
        elif label == "-":
            y += 9.25

        hover: bool = False
        if Helper.is_point_in_rect(self.mouse.x, self.mouse.y, x, y, w, h):
            hover = True

        # Set state to dynamically use themes
        state = "-disabled" if disabled else "-hover" if hover else ""

        text_color = "#868290" if disabled else "accent"
        bg_color = "#3b3842" if disabled else "#3b3050" if hover else "#2a2238"

        # Background
        self.panel.fill_rect(x, y, w, h, bg_color)

        border_color = "#868290" if disabled else "accent"

        self.panel.fill_rect(x + (w - 2), y, 2, h, border_color)
        # self.panel.fill_rect(x, y, 2, h, border_color)
        if label == "+":
            self.panel.draw_text(x + 5, y + (h / 2) + 0.5, label, 13, text_color)
        if label == "-":
            self.panel.draw_text(x + 5, y + (h / 2) + 0.5, label, 13, text_color)

        # Click listener
        if not disabled:
            for c in self.click_list:
                if Helper.is_point_in_rect(c.x, c.y, x, y, w, h):
                    click_fn(*[label])
