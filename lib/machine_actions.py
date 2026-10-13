from dataclasses import dataclass, asdict, fields
from types_def import CargoTypes
from typing import Union


# ---------- DATACLASSES ----------
@dataclass
class StatusSetAction:
    status: str
    level: str = "info"
    action: str = "status_set"


@dataclass
class MountModuleAction:
    module_slot: int
    module_id: str
    action: str = "mount_module"


@dataclass
class UnmountModuleAction:
    module_slot: int
    action: str = "unmount_module"


@dataclass
class InstallItemAction:
    module_slot: int
    internal_index: int
    item_id: int
    action: str = "install_item"


@dataclass
class UninstallItemAction:
    module_slot: int
    internal_index: int
    action: str = "uninstall_item"


@dataclass
class DockAction:
    station: str
    action: str = "dock"


@dataclass
class CargoConnectAction:
    type: CargoTypes
    target_id: str
    action: str = "cargo_connect"


@dataclass
class CargoDisconnectAction:
    type: CargoTypes
    action: str = "cargo_disconnect"


@dataclass
class CargoCompactAction:
    action: str = "cargo_compact"


@dataclass
class CargoDiscardAction:
    rack_index: str
    action: str = "cargo_discard"


@dataclass
class CargoRequestAction:
    item_id: str
    count: int
    action: str = "cargo_request"


@dataclass
class CargoSendAction:
    item_id: str
    count: int
    action: str = "cargo_send"


@dataclass
class TargetSetAction:
    coords: tuple[int, int]
    action: str = "target_set"


@dataclass
class BrakeAction:
    action: str = "brake"


@dataclass
class ScanAction:
    action: str = "scan"


@dataclass
class SurveyAction:
    site_id: str
    action: str = "survey"


@dataclass
class MineAction:
    action: str = "mine"


@dataclass
class FollowAction:
    type: str
    target_id: str
    action: str = "follow"


# ---------- TYPES ----------
MapAction = Union[TargetSetAction, FollowAction]
VehicleAction = Union[
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
]

Actions = Union[MapAction, VehicleAction]

# ---------- REGISTRY ----------
MACHINE_ACTION_REGISTRY: dict[str, type] = {
    "mount_module": MountModuleAction,
    "unmount_module": UnmountModuleAction,
    "install_item": InstallItemAction,
    "uninstall_item": UninstallItemAction,
    "dock": DockAction,
    "cargo_connect": CargoConnectAction,
    "cargo_disconnect": CargoDisconnectAction,
    "cargo_compact": CargoCompactAction,
    "cargo_discard": CargoDiscardAction,
    "cargo_request": CargoRequestAction,
    "cargo_send": CargoSendAction,
    "target_set": TargetSetAction,
    "brake": BrakeAction,
    "scan": ScanAction,
    "survey": SurveyAction,
    "mine": MineAction,
    "follow": FollowAction,
}


def deserialize_action(data: dict) -> Actions | None:
    action_type = data.get("action")
    cls = MACHINE_ACTION_REGISTRY.get(action_type)
    if not cls:
        return None

    allowed_names = {f.name for f in fields(cls)}
    valid_fields = {k: v for k, v in data.items() if k in allowed_names}
    return cls(**valid_fields)
