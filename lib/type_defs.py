from typing import Literal

# ---------- LIBRARY ----------
# --- DB ---
DBType = Literal["config", "data", "task"]
DBType = Literal["config", "data", "task"]

# --- TASK ---
TaskKey = Literal["active", "queue", "history"]

# ---------- PANELS ----------
# ----- MAP -----
MapConfigKey = Literal["enabled", "zoom", "biomes", "outposts", "locations", "vehicles", "drones"]
MapDataKey = Literal["center", "follow"]
# ----- MAIN -----

# ---------- MACHINES ----------
RoverConfigKey = Literal["throttle", "auto_charge", "scan_range"]
RoverDataKey = Literal["target_pos", "battery_warning", "cargo_filter"]


# ---------- OTHER ----------
