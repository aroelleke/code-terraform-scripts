from panel_wrapper import PanelWrapper
from vehicle import VehicleController


class VehicleIOPanel(PanelWrapper):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")

        self.target: VehicleController

    def prepare(self, target: VehicleController, **_):
        self.target = target

    def render(self):
        self.c.save()
