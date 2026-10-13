from base_controller import BaseController
from dataclasses import dataclass
from machine_store import MachineStore
from routine_store import RoutineStore
from machine_actions import (
    MountModuleAction,
    UnmountModuleAction,
    InstallItemAction,
    UninstallItemAction,
    DockAction,
    CargoConnectAction,
    CargoDisconnectAction,
    CargoCompactAction,
    CargoDiscardAction,
    CargoRequestAction,
    CargoSendAction,
    TargetSetAction,
    BrakeAction,
    ScanAction,
    SurveyAction,
    MineAction,
)


@dataclass
class VehicleConfig:
    throttle: float = 0.5


# TODO: rework whole logic based on new jobs and routines logic
class VehicleController(BaseController):
    def __init__(self, ref: Rover | Pioneer):
        super().__init__(ref)
        self.ref: Rover | Pioneer

        self.store: MachineStore[VehicleConfig] = MachineStore(f"vehicle.{ref.id}", VehicleConfig)
        self.routines = RoutineStore("vehicle")

        self.planet: Nocturna = get_component("nocturna")
        self.journal: Journal = get_component("journal")
        self.outpost_network: OutpostNetwork = get_component("outpost_network")

    def iteration(self):
        self.store.refresh()

        print(self.ref.current_station())

        action = self.store.get_current_action()

        if not action:
            return

        is_done = self.execute_action(action)
        if is_done:
            self.store.advance_step()

    def execute_action(self, action: Actions) -> bool:
        match action:
            case MountModuleAction(module_slot=slot, module_id=mod_id):
                return self.mount_module(slot, mod_id)
            case UnmountModuleAction(module_slot=slot):
                return self.mount_module(slot, mod_id)
            case InstallItemAction(module_slot, internal_index, item_id):
                return self.install_item(module_slot, internal_index, item_id)
            case UninstallItemAction(module_slot, internal_index):
                return self.uninstall_item(module_slot, internal_index)
            case DockAction(station):
                return self.dock(station)
            case CargoConnectAction(type, target_id):
                return self.cargo_connect(type, target_id)
            case CargoDisconnectAction(type):
                return self.cargo_disconnect(type)
            case CargoCompactAction():
                return self.cargo_compact()
            case CargoDiscardAction():
                return self.cargo_discard()
            case CargoRequestAction(item_id, count):
                return self.cargo_request(item_id, count)
            case CargoSendAction(item_id, count):
                return self.cargo_send(item_id, count)
            case TargetSetAction(coords):
                return self.target_set(coords)
            case BrakeAction():
                return self.brake()
            case ScanAction():
                return self.scan()
            case SurveyAction():
                return self.survey()
            case MineAction():
                return self.mine()
            case _:
                return True

    def mount_module(self, module_index: int, item_id: str) -> bool:
        result = self.ref.mount(module_index, item_id)
        return result.status == "ok"

    def unmount_module(self, module_index: int) -> bool:
        result = self.ref.unmount(module_index)
        return result.status == "ok"

    def install_item(self, module_slot: int, internal_index: int, item_id: int) -> bool:
        result = self.ref.install(module_slot, interal_index, item_id)
        return result.status == "ok"

    def uninstall_item(self, module_slot: int, internal_index: int) -> bool:
        result = self.ref.uninstall(module_slot, interal_index)
        return result.status == "ok"

    def dock(self, station: str) -> bool:
        # TODO: really fix that either the id is gotten or this is cleaned up
        outpost: Outposts = get_component_by_name(station)
        outpost = get_component("outpost_home")
        buildings = outpost.buildings("charging_station")
        building = buildings[0]

        result = self.ref.dock(building.id)
        return self.ref.battery.level() == 1

    def cargo_connect(self, type: CargoTypes, target_id: str) -> bool:
        result = None
        match type:
            case "input":
                result = self.ref.input.connect(target_id)
            case "output":
                result = self.ref.output.connect(target_id)
        return result.status == "ok"

    def cargo_disconnect(self, rack_index: int) -> bool:
        result = None
        match type:
            case "input":
                result = self.ref.input.disconnect()
            case "output":
                result = self.ref.output.disconnect()
        return result.status == "ok"

    def cargo_compact(self, rack_index: int) -> bool:
        result = self.ref.cargo.compact()
        return result.status == "ok"

    def cargo_discard(self, rack_index: int) -> bool:
        result = self.ref.cargo.discard(rack_index)
        return result.status == "ok"

    def cargo_request(self, item_id: str, count: int) -> bool:
        result = self.ref.input.take(item_id, count)
        return result.status == "ok"

    def cargo_send(self, item_id: str, count: int) -> bool:
        result = self.ref.output.send(item_id, count)
        return result.status == "ok"

    def target_set(self, coords: tuple[int, int]) -> bool:
        result = self.ref.nav.set_target(*coords)
        self.ref.nav.set_throttle(self.store.config.throttle)

        return self.ref.nav.get_distance_to(*coords) == 0

    def brake(self) -> bool:
        result = self.ref.nav.brake()
        return result.status == "ok"

    def scan(self) -> bool:
        result = self.ref.sonar.scan()
        return result.status == "ok"

    def survey(self) -> bool:
        result = self.ref.sonar.survey(self.task["site_id"])
        return result.status == "ok"

    def mine(self) -> bool:
        result = self.ref.drill.mine()
        return result.status == "ok"

    def has_module(self, module_id: str) -> bool:
        return bool([module.module_id for module in self.ref.modules() if module.module_id == module_id])

    def has_nav(self) -> bool:
        return self.has_module("nav_module")

    def is_home(self) -> bool:
        if not self.has_nav():
            return True

        pos = self.ref.nav.get_position()
        return pos.x == 0 and pos.y == 0

    def nearest_outpost(self) -> OutpostRef:
        if self.has_nav():
            pos = self.ref.nav.get_position()
            return self.outpost_network.nearest(pos.x, pos.y)

    def modules(self) -> dict:
        modules = dict()
        for module in self.ref.modules():
            modules[module.type] = module.module_id

        return modules
