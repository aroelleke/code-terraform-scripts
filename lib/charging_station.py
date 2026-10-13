from base_controller import BaseController
from dataclasses import dataclass
from helper import clamp, calculate_next_step_of_value
from machine_store import MachineStore
from pioneer import PioneerController
from rover import RoverController
from vehicle import VehicleController


@dataclass
class ChargingStationConfig:
    enable_auto_queue: bool = True
    enable_stepwise_auto_charge: bool = True
    auto_charge_step_size: float = 0.2
    auto_charge_max_level: float = 1
    auto_charge_min_level: float = 0


class ChargingStationController(BaseController):
    def __init__(self, ref: ChargingStation):
        super().__init__(ref)
        self.ref: ChargingStation

        self.store: MachineStore[ChargingStationConfig] = MachineStore(f"charging_station.{ref.id}", ChargingStationConfig)

        self.journal: Journal = get_component("journal")
        self.fleet: Fleet = get_component("fleet")

        self.docked_vehicles: dict[str, VehicleController] = {}

    def iteration(self):
        self.update_vehicles()

        # self.action(action, data)

        # if self.store.config.enable_auto_queue:
        self.auto_queue()

    def update_vehicles(self):
        vehicles = self.ref.get_docked()

        # Clean list of dead entries
        self.docked_vehicles = {id: item for id, item in self.docked_vehicles.items() if id in vehicles}

        # Add new
        for id in vehicles:
            if id not in self.docked_vehicles:
                component = get_component(id)

                match component.type_id:
                    case "rover":
                        self.docked_vehicles[id] = RoverController(component)
                    case "pioneer":
                        self.docked_vehicles[id] = PioneerController(component)

    # def action(self, action: str, data: dict):
    #     match action:
    #         case "add_to_queue":
    #             self.add_to_queue(data["target_id"], data["target_level"])
    #         case "remove_from_queue":
    #             self.remove_from_queue(data["target_id"])
    #         case "clear_queue":
    #             self.clear_queue()

    def add_to_queue(self, vehicle_id: str, level: number):
        self.ref.charge(vehicle_id, level)

    def remove_from_queue(self, vehicle_id: str):
        self.ref.stop(vehicle_id)

    def clear_queue(self):
        self.ref.clear_queue()

    def auto_queue(self):
        active = self.ref.get_active()
        bays = self.ref.get_bay_count()

        if len(active) == bays:
            return

        queue = self.ref.get_queue()

        for id, vehicle in self.docked_vehicles.items():
            battery_level = vehicle.ref.battery.level()

            if id in active:
                continue
            if id in queue:
                continue
            if battery_level == 1:
                continue
            if vehicle.ref.status() == "charging":
                continue

            max_level = self.store.config.auto_charge_max_level
            min_level = self.store.config.auto_charge_min_level

            if self.store.config.enable_stepwise_auto_charge:
                next_step = calculate_next_step_of_value(battery_level, self.store.config.auto_charge_step_size)
                max_level = clamp(next_step, min_level, max_level)

            self.ref.charge(id, max_level)
