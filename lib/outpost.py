from base_controller import BaseController
from dataclasses import dataclass
from machine_store import MachineStore


@dataclass
class OutpostConfig:
    pass


class OutpostController(BaseController):
    def __init__(self, ref: Outpost):
        super().__init__(ref)
        self.ref: Outpost

        self.store: MachineStore[OutpostConfig] = MachineStore(f"outpost.{ref.id}", OutpostConfig)

        self.power_control: PowerControl = get_component("power_control")
        self.grid: PowerGrid = self.power_control.grid(self.ref.id)
