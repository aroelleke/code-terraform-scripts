from page_panel import PagePanel
from vehicle import VehicleController
from vehicle_general_panel import VehicleGeneralPanel
from vehicle_io_panel import VehicleIOPanel
from vehicle_modules_panel import VehicleModulesPanel
from vehicle_power_panel import VehiclePowerPanel
from vehicle_task_panel import VehicleTaskPanel
from vehicle_task_active_panel import VehicleTaskActivePanel
from vehicle_task_builder_panel import VehicleTaskBuilderPanel


class VehiclePanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")

        self.panels = {
            "General": VehicleGeneralPanel(self.panel),
            "Modules": VehicleModulesPanel(self.panel),
            "Power": VehiclePowerPanel(self.panel),
            # "Task": VehicleTaskPanel(self.panel),
            "Active": VehicleTaskActivePanel(self.panel),
            "Builder": VehicleTaskBuilderPanel(self.panel),
            # "I/O": VehicleIOPanel(self.panel),
        }
        for p in self.panels.values():
            p.parent = self

        self.target: VehicleController
        # self.vehicle_list: list[VehicleRef]
        # self.outpost_list: list[OutpostRef]
        # self.location_list: list[PointOfInterest]
        # self.drone_list: list[DroneRef]

    def prepare(
        self,
        target: VehicleController = None,
        # vehicle_list: list[VehicleRef] = [],
        # outpost_list: list[OutpostRef] = [],
        # location_list: list[PointOfInterest] = [],
        # drone_list: list[DroneRef] = [],
        **_,
    ):
        super().prepare(**_)

        self.target = target
        # self.vehicle_list: list[VehicleRef] = vehicle_list
        # self.outpost_list: list[OutpostRef] = outpost_list
        # self.location_list: list[PointOfInterest] = location_list
        # self.drone_list: list[DroneRef] = drone_list

    def render(self, **_):
        super().render(**_)

    def get_tab_data(self, tab: str) -> dict:
        return {"target": self.target}
        # match tab:
        #     case "General":
        #         return {"target": self.target}
        #     case "Modules":
        #         return {"target": self.target}
        #     case "Power":
        #         return {"target": self.target}
        #     case "Inventory":
        #         return {"target": self.target}
        #     case "Task":
        #         return {"target": self.target}
        #     case "I/O":
        #         return {"target": self.target}
        #     case _:
        #         return {}

    def draw_config(self):
        self.c.save(True)

        self.c.y += 40
        self.panel.card(self.c.x, self.c.y, 300, 150, "CONFIG")

        self.c.load()
