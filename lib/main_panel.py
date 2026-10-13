from panel import PanelBase, TableColumn, Column
from rover import RoverController
from pioneer import PioneerController
from outpost import OutpostController
from config_database import Config
from user_stubs import MainPanelType


class MainPanel(PanelBase):
    def __init__(self, panel: Panel):
        super().__init__(panel)

        self.config: Config = Config("control_room", "control_room")
        self.fleet: Fleet = get_component("fleet")
        self.outpost_network: OutpostNetwork = get_component("outpost_network")

        self.show_config: bool = False
        self.current_view: MainPanelType = "outpost"

    def handle_sync(self):
        if not self.config.get("sync"):
            return

        view = self.config.get("current_view")
        if view:
            self.current_view = view
