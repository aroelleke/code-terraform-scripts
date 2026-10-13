from grid_panel import GridPanel
from inventory_panel import InventoryPanel
from outpost import OutpostController
from outpost_panel import OutpostPanel
from page_panel import PagePanel
from pioneer import PioneerController
from rover import RoverController
from shop_panel import ShopPanel
from vehicle_panel import VehiclePanel
from machine_store import MachineStore
from map_panel import MapConfig
from helper import position_to_coords


# TODO:
# -
class OverviewPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "overview", True)

        self.map_store: MachineStore[MapConfig] = MachineStore("panel.map", MapConfig)

        self.panels = {
            "Outpost": OutpostPanel(panel),
            "Vehicle": VehiclePanel(panel),
            # "Grid": GridPanel(panel),
            "Inventory": InventoryPanel(self.panel),
            "Shop": ShopPanel(panel),
        }

        # Components
        self.fleet: Fleet = get_component("fleet")
        self.outpost_network: OutpostNetwork = get_component("outpost_network")
        self.power_control: PowerControl = get_component("power_control")
        self.planet: Nocturna = get_component("nocturna")

        # Data
        self.target_list: dict[str, list[str]] = {}
        self.target: OutpostController | VehicleController | PowerGrid = None
        self.outpost_list: list[OutpostRef] = []
        self.vehicle_list: list[VehicleRef] = []
        self.grid_list: list[PowerGrid] = []

    def prepare(self, **_):
        super().prepare(**_)

        self.map_store.refresh()

        self.outpost_list = self.outpost_network.outposts()
        self.vehicle_list = self.fleet.vehicles()
        self.grid_list = self.power_control.grids()

        self.set_target_list()

    def set_target_list(self):
        self.target_list["Outpost"] = [item.id for item in self.outpost_list]
        self.target_list["Vehicle"] = [item.id for item in self.vehicle_list]
        self.target_list["Grid"] = [item.anchor_id for item in self.grid_list]

    def set_tab(self, value: str, **_):
        super().set_tab(value)

        self.update_target()

    def get_tab_data(self, tab: str) -> dict:
        match tab:
            case "Outpost":
                return {"target": self.target, "outpost_list": self.outpost_list}
            case "Vehicle":
                return {"target": self.target, "vehicle_list": self.vehicle_list}
            case "Grid":
                return {"target": self.target, "grid_list": self.grid_list}
            case _:
                return {}

    def render(self, **_):
        super().render(**_)

        self.draw_header()

    def get_target_list(self, tab: str = None):
        if not tab:
            tab = self.tab

        if self.tab in self.target_list:
            return self.target_list[self.tab]

    def has_target_list(self, tab: str = None):
        if not tab:
            tab = self.tab

        return self.tab in self.target_list

    def draw_header(self):
        self.c.reset_y()

        if self.has_target_list():
            self.draw_map_actions()
            self.draw_target_selection()

        self.c.load()
        self.c.save(True)

    def draw_map_actions(self):
        if not self.target:
            return

        self.c.save()

        self.c.x = self.panel.width() - 230

        map_job = self.map_store.get_current_action()
        new_actions = []

        coords: tuple[int, int] = [0, 0]
        match self.tab:
            case "Outpost":
                coords = self.target.ref.coords()
            case "Vehicle":
                if self.target.has_nav():
                    coords = position_to_coords(self.target.ref.nav.get_position())
            case "Drone":
                coords = position_to_coords(self.target.ref.position())

        viewing: bool = bool(map_job) and map_job.action == "target_set" and map_job.coords == coords
        if viewing:
            coords = [0, 0]

        def click(_):
            new_actions.append({"action": "target_set", "coords": coords})

        self.c.save()
        self.c.y += 3
        self.draw_button("View", click_fn=click, disabled=True if viewing else False)
        self.c.x += -85

        if self.tab != "Outpost":
            following: bool = map_job.action == "follow" and map_job.target_id == self.target.ref.id and bool(map_job)
            self.c.y += 2
            # TODO: check if this causes problems
            follow = self.panel.switch(f"{self.key}.map_follow", self.c.x, self.c.y, default_on=following, size=15)
            # if following:
            #     self.panel.set_switch(f"{self.key}.map_follow", True)

            self.c.x += 34
            self.panel.draw_text(self.c.x, self.c.y + 4, "Follow", 9, "success" if follow else "bg-surface")
            self.panel.draw_text(self.c.x, self.c.y + 12, "Unfollow", 9, "error" if not follow else "bg-surface")
            if following and not follow:
                if self.target.has_nav():
                    new_actions = [{"action": "target_set", "coords": coords}]
                else:
                    new_actions = [{"action": "target_set", "coords": [0, 0]}]
            elif not following and follow:
                new_actions = [{"action": "follow", "type": self.tab.lower(), "target_id": self.target.ref.id}]

        self.c.load()
        if new_actions:
            self.map_store.assign_job(actions=new_actions)

    def draw_target_selection(self):
        self.c.save()

        self.c.x = self.panel.width() - 180
        key = f"{self.key}.target-selection"

        target_list = self.get_target_list()
        target_id = self.panel.combo(
            key,
            self.c.x,
            self.c.y + 1,
            175,
            target_list,
            target_list[0] if target_list else None,
            size=23,
        )

        # self.c.x -= 60
        # self.panel.draw_text(self.c.x, self.c.y + 13, "Target:", 14, "accent")

        if target_id:
            self.update_target(target_id)

    def draw_config(self):
        self.c.save(True)

        self.c.y += 40
        self.panel.card(self.c.x, self.c.y, 300, 150, "CONFIG")

        self.c.load()

    def update_target(self, target_id: str = None):
        if target_id == None:
            if self.tab in self.target_list:
                target_id = self.target_list[self.tab][0]

        if self.target and self.target.ref.id == target_id:
            return

        if target_id:
            ref = get_component(target_id)
            match self.tab:
                case "Outpost":
                    self.target = OutpostController(ref)
                case "Vehicle":
                    match ref.type_id:
                        case "rover":
                            self.target: RoverController = RoverController(ref)
                        case "pioneer":
                            self.target: PioneerController = PioneerController(ref)
        else:
            self.target = None
