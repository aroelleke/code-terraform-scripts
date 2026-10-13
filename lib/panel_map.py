from config_database import Config
from helper import position_to_coords
from map_panel import MapPanelElement
from outpost import OutpostController
from panel_wrapper import PanelElement
from vehicle import VehicleController


class PanelMapController(PanelWrapper):
    def __init__(self, panel: Panel):
        super().__init__(panel, "main")
        self.config: Config = Config(self.key, self.key)

        self.fleet: Fleet = get_component("fleet")
        self.outpost_network: OutpostNetwork = get_component("outpost_network")
        self.power_control: PowerControl = get_component("power_control")
        self.planet: Nocturna = get_component("nocturna")

        self.map_element: MapPanelElement = MapPanelElement(self.panel)
        self.root = True

        self.margin: (int, int, int, int) = (5, 2, 5, 0)

        self.target: OutpostController | VehicleController | PowerGrid = None
        self.click_list: list[PanelClick] = []
        self.outpost_list: list[OutpostRef] = []
        self.location_list: list[PointOfInterest] = []
        self.vehicle_list: list[VehicleRef] = []
        self.drone_list: list[DroneRef] = []
        self.grid_list: list[PowerGrid] = []

    def prepare(self, **_):
        self.update_clicks()
        self.update_outposts()
        self.update_locations()
        self.update_vehicles()
        self.update_drones()
        self.update_grids()

    def update_clicks(self):
        self.click_list = self.panel.clicks()

    def update_outposts(self):
        self.outpost_list = self.outpost_network.outposts()

    def update_vehicles(self):
        self.vehicle_list = self.fleet.vehicles()

    def update_grids(self):
        self.grid_list = self.power_control.grids()

    def update_locations(self):
        self.location_list = self.planet.points_of_interest()

    def update_drones(self):
        self.drones = self.fleet.drones()

    def render(self):
        self.draw_map()

    def get_page_dimensions(self):
        return [self.c.x, self.c.y, self.panel.width() - self.c.x, self.panel.height() - self.c.y]

    def draw_map(self):
        dims = [
            self.c.x,
            self.c.y,
            0,
            0,
        ]
        data = {
            "outpost_list": self.outpost_list,
            "location_list": self.location_list,
            "vehicle_list": self.vehicle_list,
            "drone_list": self.drone_list,
            "center_coords": self.config.get("map.center_coords"),
            "click_list": self.click_list,
        }
        self.map_element.run(dims, data)
