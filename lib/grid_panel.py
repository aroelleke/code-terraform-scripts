from outpost_general_panel import OutpostGeneralPanel
from panel_wrapper import PanelWrapper


class GridPanel(PanelWrapper):
    def __init__(self, panel: Panel):
        super().__init__(panel, "grid")
        self.panels = {
            "General": OutpostGeneralPanel(self.panel),
        }

        self.target: PowerGrid
        self.outpost_list: list[OutpostRef]

    def prepare(self, target: PowerGrid, **_):
        self.grid = target

    def render(self):
        pass
