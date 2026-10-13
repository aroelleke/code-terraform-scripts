from helper import is_point_in_rect
from page_panel import PagePanel
from vehicle import VehicleController


class VehiclePowerPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")

        self.target: VehicleController

    def prepare(self, target: VehicleController = None, **_):
        super().prepare(**_)

        self.target = target

    def render(self, **_):
        super().render(**_)

        self.c.y += 20
        self.c.save(True)

        self.draw_holders()

    def draw_holders(self):
        self.panel.label(self.c.x + 12, self.c.y, "BATTERY HOLDERS", "caption")

        self.c.x += 20
        self.c.y += 10

        self.c.set_origin("x")

        match self.target.ref.type_id:
            case "pioneer":
                holder_list: list[Holder] = self.target.ref.battery.holders()

                for i, holder in enumerate(holder_list):
                    self.draw_holder(i, holder)
                    self.c.x += 55

            case "rover":
                pass

    def is_holder_empty(self, holder):
        for bat in holder.batteries:
            if bat:
                return False
        return True

    def draw_holder(self, index: int, holder: Holder):
        w, h = 400, 200

        hover: bool = False
        if is_point_in_rect(self.mouse.x, self.mouse.y, self.c.x, self.c.y, self.c.x + w, self.c.y + h):
            hover = True

        empty = self.is_holder_empty(holder)
        level = 0
        if holder.capacity > 0:
            level = holder.wh / holder.capacity
        level = 0.9

        bg_color: str = "hsl(265, 24%, 18%)"
        border_color: str = "hsl(265, 90%, 78%)"
        border_width: int = 1

        if empty:
            bg_color = "hsl(113, 0%, 15%)" if not hover else "hsl(113, 0%, 16%)"
            border_color = "hsl(113, 0%, 50%)"
        elif level > 0.3:
            bg_color = "hsl(113, 24%, 15%)" if not hover else "hsl(113, 24%, 18%)"
            border_color = "hsl(113, 50%, 50%)"
        elif level > 0.1:
            bg_color = "hsl(60, 24%, 15%)" if not hover else "hsl(60, 24%, 18%)"
            border_color = "hsl(60, 50%, 50%)"
        else:
            bg_color = "hsl(8, 24%, 15%)" if not hover else "hsl(8, 24%, 18%)"
            border_color = "hsl(8, 50%, 50%)"

        # BG
        self.panel.fill_rect(self.c.x, self.c.y, w, h, bg_color)

        # Border (left, top, right, bottom)
        self.panel.draw_rect(self.c.x, self.c.y, border_width, h, border_color)
        self.panel.draw_rect(self.c.x, self.c.y, w, border_width, border_color)
        self.panel.draw_rect(self.c.x + w - border_width, self.c.y, border_width, h, border_color)
        self.panel.draw_rect(self.c.x, self.c.y + h - border_width, w, border_width, border_color)

        self.c.x += 5
        self.c.y += 10

        self.c.save(True)

        self.panel.draw_text(self.c.x, self.c.y, f"{index}:", 10, "accent")
        self.c.x += 20
        # self.c.reset_x()
        self.c.y += 20

        self.panel.draw_text(self.c.x, self.c.y, "ID", 10, "accent")
        self.c.x += 20
        self.panel.draw_text(self.c.x, self.c.y, holder.id, 11, "white")
        self.c.x += 200

        self.panel.draw_text(self.c.x, self.c.y, "Size", 10, "accent")
        self.c.x += 30
        self.panel.draw_text(self.c.x, self.c.y, f"{holder.size}", 11, "white")
        self.c.reset_x()
        self.c.y += 20

        self.panel.draw_text(self.c.x, self.c.y, "All", 10, "accent")
        self.c.x += 30
        self.panel.progress_bar(self.c.x, self.c.y - 10, 100, 20, level, "success" if level > 0.8 else "warning" if level > 0.5 else "error")
        self.c.reset_x()
        self.c.y += 40

        for i, battery in enumerate(holder.batteries):
            self.draw_holder_battery(i, battery)

    def draw_holder_battery(self, index: int, battery: Battery):
        w, h = 100, 35

        level = 0
        if battery:
            level = battery.level()
        level = 0.3 * (index + 1)

        # bg_color: str = "hsl(265, 24%, 18%)"
        # border_color: str = "hsl(265, 90%, 78%)"
        # border_width: int = 1
        # self.panel.fill_rect(self.c.x, self.c.y, w, h, "#293822")
        # self.panel.progress_bar(self.c.x, self.c.y, 150, 15)

        self.panel.draw_text(self.c.x, self.c.y, f"{index}", 10, "accent")
        self.c.x += 30
        self.panel.progress_bar(self.c.x, self.c.y - 10, 100, 20, level, "success" if level > 0.8 else "warning" if level > 0.5 else "error")
        self.c.reset_x()
        self.c.y += 40
