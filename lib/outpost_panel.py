from outpost import OutpostController
from outpost_buildings_panel import OutpostBuildingsPanel
from outpost_general_panel import OutpostGeneralPanel
from page_panel import PagePanel


# TODO:
# - show grid
# - add biology lab tab where biology lab machines can be coordinated
class OutpostPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "outpost")

        self.panels = {
            "General": OutpostGeneralPanel(self.panel),
            "Buildings": OutpostBuildingsPanel(self.panel),
        }

        self.target: OutpostController
        self.outpost_list: list[OutpostRef]

    def prepare(
        self,
        target: OutpostController = None,
        outpost_list: list[OutpostRef] = None,
        **_,
    ):
        super().prepare(**_)

        self.target = target
        self.outpost_list: list[OutpostRef] = outpost_list

    def get_tab_data(self, tab: str) -> dict:
        match tab:
            case "General":
                return {"target": self.target, "outpost_list": self.outpost_list}
            case "Buildings":
                return {"target": self.target}
            case _:
                return {}

    def draw_config(self):
        self.c.save(True)

        self.c.y += 40
        self.panel.card(self.c.x, self.c.y, 300, 150, "CONFIG")

        self.c.load()
