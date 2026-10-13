from outpost import OutpostController
from page_panel import PagePanel


class OutpostGeneralPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "outpost")

        self.target: OutpostController

    def prepare(self, target: OutpostController = None, **_):
        super().prepare(**_)

        self.target = target

    def render(self, **_):
        super().render(**_)

        self.c.save()

        if not self.target or not isinstance(self.target, OutpostController):
            return

        self.draw_info()

    def draw_info(self):
        self.c.y += 20
        self.panel.label(self.c.x + 12, self.c.y, "INFO", "muted")

        self.c.y += 20
        self.c.x += 20
        self.c.save(True)

        # ID
        self.panel.draw_text(self.c.x, self.c.y, "ID:", 13, "accent")
        self.c.x += 100
        self.panel.draw_text(self.c.x, self.c.y, f"{self.target.ref.id}", 13, "white")

        self.c.reset_x()
        self.c.y += 25

        # Name
        self.panel.draw_text(self.c.x, self.c.y, "Name:", 13, "accent")
        self.c.x += 100
        self.panel.draw_text(self.c.x, self.c.y, f"{self.target.ref.name()}", 13, "white")

        self.c.reset_x()
        self.c.y += 25

        # Coords
        self.panel.draw_text(self.c.x, self.c.y, "Coords:", 13, "accent")
        self.c.x += 100
        self.panel.draw_text(self.c.x, self.c.y, f"{self.target.ref.coords()}", 13, "white")

        self.c.reset_x()
        self.c.y += 25

        # Buildings
        self.panel.draw_text(self.c.x, self.c.y, "Buildings:", 13, "accent")
        self.c.x += 100
        self.panel.draw_text(
            self.c.x,
            self.c.y,
            f"{self.target.ref.buildings_used()}/{self.target.ref.buildings_capacity()}",
            13,
            "white" if not self.target.ref.is_full() else "warning",
        )

        self.c.reset_x()
        self.c.y += 25

        # Home
        self.panel.draw_text(self.c.x, self.c.y, "Home:", 13, "accent")
        self.c.x += 100
        self.panel.draw_text(self.c.x, self.c.y, f"{self.target.ref.is_home()}", 13, "success" if self.target.ref.is_home() else "error")

        self.c.reset_x()
        self.c.y += 25

        # Charging Station
        self.panel.draw_text(self.c.x, self.c.y, "Charge:", 13, "accent")
        self.c.x += 100
        self.panel.draw_text(self.c.x, self.c.y, f"{bool(self.target.ref.buildings('charging_station'))}", 13, "white")

        self.c.load()
