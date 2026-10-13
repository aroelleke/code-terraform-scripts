from helper import position_to_coords
from page_panel import PagePanel
from vehicle import VehicleController


class VehicleGeneralPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")

        self.target: VehicleController

    def prepare(self, target: VehicleController = None, **_):
        super().prepare(**_)

        self.target = target

    def render(self, **_):
        super().render(**_)

        self.c.y += 20
        self.draw_info()

    def draw_info(self):
        cw = 100
        ch = 20

        self.panel.label(self.c.x + 12, self.c.y, "GENERAL", "caption")

        self.c.x += 20
        self.c.y += 20

        self.c.set_origin("x")

        # Status
        self.panel.draw_text(self.c.x, self.c.y, "Status", 13)
        self.c.x += cw

        status_text_color = "success"
        if self.target.ref.status == "idle":
            status_text_color = "accent"
        elif self.target.ref.status() in ["charging", "queued"]:
            status_text_color = "error"
        elif self.target.ref.status() == "being_rescued":
            status_text_color = "error"

        self.panel.draw_text(self.c.x, self.c.y, self.target.ref.status(), 13, status_text_color)
        self.c.reset_x()
        self.c.y += ch

        # Battery
        self.panel.draw_text(self.c.x, self.c.y, "Battery", 13)
        self.c.x += cw

        bat = self.target.ref.battery.level()
        self.panel.progress_bar(self.c.x, self.c.y - 8, 60, 15, bat, self.get_battery_color(bat))
        level = "{:.2f}".format(bat * 100)
        self.panel.draw_text(self.c.x + 18, self.c.y, f"{level}%", 13, "black")
        self.c.reset_x()
        self.c.y += ch

        # Position
        self.panel.draw_text(self.c.x, self.c.y, "Position", 13)
        self.c.x += cw

        if self.target.has_nav():
            coords = position_to_coords(self.target.ref.nav.get_position())
            self.panel.draw_text(self.c.x, self.c.y, f"[{'{:.1f}'.format(coords[0])}, {'{:.1f}'.format(coords[1])}]", 13)
        else:
            self.panel.draw_text(self.c.x, self.c.y, "nav missing", 13, "error")
        self.c.reset_x()
        self.c.y += ch

        # Outpost
        self.panel.draw_text(self.c.x, self.c.y, "Outpost", 13)
        self.c.x += cw

        try:
            outpost = self.target.nearest_outpost()
            outpost_coords = outpost.coords()
            distance = self.target.ref.nav.get_distance_to(outpost_coords[0], outpost_coords[1])

            if distance < 2:
                self.panel.draw_text(self.c.x, self.c.y, outpost.name, 13, "success")
            else:
                self.panel.draw_text(self.c.x, self.c.y, "...", 13, "warning")
        except:
            self.panel.draw_text(self.c.x, self.c.y, "nav missing", 13, "error")
        self.c.reset_x()
        self.c.reset_y()

    def get_battery_color(self, charge: number) -> str:
        return "success" if charge > 0.5 else "warn" if charge > 0.2 else "error"
