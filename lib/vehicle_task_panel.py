from dataclasses import fields, is_dataclass
from machine_actions import MACHINE_ACTION_REGISTRY, Actions, deserialize_action
from page_panel import PagePanel
from vehicle import VehicleController


class VehicleTaskPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")

        self.target: VehicleController

        # Builder State
        self.selected_action_name: str = "target_set"
        self.builder_params: dict = {}
        self.staged_actions: list[dict] = []
        self.selected_routine_name: str | None = None
        self.builder_loop: bool = True

    def prepare(self, target: VehicleController = None, **_):
        super().prepare(**_)

        self.target = target
        if self.target:
            self.target.store.refresh()

    def render(self, **_):
        super().render(**_)

        if not self.target:
            self.panel.draw_text(self.c.x + 20, self.c.y + 20, "No vehicle selected", 13, "error")
            return

        self.c.y += 20
        self.c.save(True)

        # LINKEN BLOCK ZEICHNEN
        self.draw_current_job()
        self.c.y += 20
        self.draw_routine_list()

        # ZURÜCK ZUM SPALTEN-URSPRUNG & OFFSET NACH RECHTS
        self.c.load()
        self.c.x += 380
        self.c.save(True)

        # RECHTEN BLOCK (BUILDER) ZEICHNEN
        self.draw_action_builder()

        self.c.load()

    # -------------------------------------------------------------
    # LINKE SPALTE: ACTIVE JOB & PRESETS
    # -------------------------------------------------------------

    def draw_current_job(self):
        cw, ch = 340, 190
        self.panel.label(self.c.x + 12, self.c.y, "ACTIVE JOB", "caption")

        self.c.x += 10
        self.c.y += 15

        job = self.target.store.job

        # Box Background
        self.panel.fill_rect(self.c.x, self.c.y, cw, ch, "#1e1f27")
        self.panel.draw_rect(self.c.x, self.c.y, 2, ch, "accent" if job else "#40424f")

        if not job:
            self.panel.draw_text(self.c.x + 20, self.c.y + 25, "Status:", 12, "accent")
            self.panel.draw_text(self.c.x + 75, self.c.y + 25, "Idle (No Job Assigned)", 12, "warning")
            self.c.y += ch
            return

        routine_name = job.get("routine_name") or "Custom Job"
        step_idx = job.get("step_index", 0)
        actions = job.get("actions", [])
        loop = job.get("loop", False)

        self.panel.draw_text(self.c.x + 15, self.c.y + 15, "Routine:", 11, "accent")
        self.panel.draw_text(self.c.x + 80, self.c.y + 15, routine_name, 12, "white")

        self.panel.draw_text(self.c.x + 15, self.c.y + 35, "Loop:", 11, "accent")
        self.panel.draw_text(self.c.x + 80, self.c.y + 35, "Enabled" if loop else "Single Run", 11, "success" if loop else "text-bright")

        progress = (step_idx + 1) / len(actions) if actions else 0
        self.panel.draw_text(self.c.x + 15, self.c.y + 55, "Progress:", 11, "accent")
        self.panel.progress_bar(self.c.x + 80, self.c.y + 53, 140, 14, progress, "success")
        self.panel.draw_text(self.c.x + 230, self.c.y + 55, f"{step_idx + 1} / {len(actions)}", 11, "text-bright")

        # Erste Aktionen als Vorschau
        for i, act in enumerate(actions[:3]):
            is_active = i == step_idx
            act_color = "success" if is_active else "#6e6e6e"
            prefix = "▶" if is_active else "•"
            label = f"{prefix} [{i + 1}] {act.get('action')}"
            self.panel.draw_text(self.c.x + 15, self.c.y + 80 + (i * 20), label, 11, act_color)

        # Cancel Button
        self.c.save()
        self.c.x += cw - 105
        self.c.y += ch - 35
        self.draw_button("Cancel Job", self.on_cancel_job, options={"w": 90, "h": 24})
        self.c.load()

        self.c.y += ch

    def draw_routine_list(self):
        cw = 340
        self.panel.label(self.c.x + 2, self.c.y, "PRESET ROUTINES", "caption")
        self.c.y += 20

        routines = self.target.routines.all()
        routine_names = list(routines.keys())

        if not routine_names:
            self.panel.draw_text(self.c.x + 10, self.c.y + 5, "No saved routines found", 11, "accent")
            return

        selected = self.panel.combo(
            f"{self.key}.routine_select",
            self.c.x + 10,
            self.c.y,
            190,
            routine_names,
            self.selected_routine_name or routine_names[0],
            size=22,
        )
        if selected:
            self.selected_routine_name = selected

        # Load & Run Button neben der Combo
        self.c.save()
        self.c.x += 215
        self.draw_button("Load & Run", self.on_load_routine, options={"w": 95, "h": 22})
        self.c.load()

    # -------------------------------------------------------------
    # RECHTE SPALTE: ACTION & JOB BUILDER
    # -------------------------------------------------------------

    def draw_action_builder(self):
        bw, bh = 430, 440
        self.panel.label(self.c.x + 12, self.c.y, "ACTION & JOB BUILDER", "caption")

        self.c.x += 10
        self.c.y += 15

        # Hintergrundbox
        self.panel.fill_rect(self.c.x, self.c.y, bw, bh, "#1e1f27")
        self.panel.draw_rect(self.c.x, self.c.y, 2, bh, "accent")

        available_actions = list(MACHINE_ACTION_REGISTRY.keys())

        # 1. Action Dropdown
        self.c.y += 12
        self.panel.draw_text(self.c.x + 15, self.c.y + 5, "Action:", 11, "accent")

        chosen_action = self.panel.combo(
            f"{self.key}.action_type_combo",
            self.c.x + 75,
            self.c.y,
            180,
            available_actions,
            self.selected_action_name,
            size=22,
        )
        if chosen_action and chosen_action != self.selected_action_name:
            self.selected_action_name = chosen_action
            self.builder_params.clear()

        self.c.y += 35

        # 2. Dynamische Parameter
        self.draw_parameter_inputs(bw)

        # 3. Queue der hinzugefügten Aktionen
        self.draw_staged_queue(bw)

    def draw_parameter_inputs(self, bw: int):
        action_cls = MACHINE_ACTION_REGISTRY.get(self.selected_action_name)
        if not action_cls or not is_dataclass(action_cls):
            return

        self.c.set_origin("x")

        # Feste Definition aller Zahlenfelder über alle Dataclasses hinweg
        INT_FIELDS = {
            "module_slot",
            "internal_index",
            "count",
            "duration",
            "power",
            "radius",
            "item_id",
            "rack_index",
        }

        for f in fields(action_cls):
            if f.name == "action":
                continue

            self.panel.draw_text(self.c.x + 15, self.c.y + 6, f"{f.name}:", 11, "white")

            # 1. Spezialbehandlung: Coords Tuple (X und Y getrennt)
            if f.name == "coords":
                coords = self.builder_params.get("coords", [0, 0])
                if not isinstance(coords, (list, tuple)):
                    coords = [0, 0]

                # X Input
                self.panel.draw_text(self.c.x + 80, self.c.y + 6, "X", 10, "accent")
                raw_x = self.panel.text_field(
                    f"{self.key}.coord_x",
                    self.c.x + 95,
                    self.c.y,
                    60,
                    str(coords[0]),
                )

                # Y Input
                self.panel.draw_text(self.c.x + 165, self.c.y + 6, "Y", 10, "accent")
                raw_y = self.panel.text_field(
                    f"{self.key}.coord_y",
                    self.c.x + 180,
                    self.c.y,
                    60,
                    str(coords[1]),
                )

                try:
                    val_x = int(raw_x) if raw_x is not None else coords[0]
                except (ValueError, TypeError):
                    val_x = coords[0]

                try:
                    val_y = int(raw_y) if raw_y is not None else coords[1]
                except (ValueError, TypeError):
                    val_y = coords[1]

                self.builder_params["coords"] = (val_x, val_y)

            # 2. Ganze Zahlen (reiner Namens- und Instanzvergleich, kein f.type)
            elif f.name in INT_FIELDS or isinstance(getattr(f, "default", None), int):
                cur_val = self.builder_params.get(
                    f.name,
                    getattr(f, "default", 0) if not callable(getattr(f, "default_factory", None)) else 0,
                )
                if not isinstance(cur_val, int):
                    try:
                        cur_val = int(cur_val)
                    except (ValueError, TypeError):
                        cur_val = 0

                raw_val = self.panel.text_field(
                    f"{self.key}.input_{f.name}",
                    self.c.x + 80,
                    self.c.y,
                    80,
                    str(cur_val),
                )
                try:
                    self.builder_params[f.name] = int(raw_val) if raw_val is not None else cur_val
                except (ValueError, TypeError):
                    self.builder_params[f.name] = cur_val

            # 3. Strings & Textfelder
            else:
                default_str = getattr(f, "default", "")
                if default_str is None or callable(getattr(f, "default_factory", None)):
                    default_str = ""
                cur_val = self.builder_params.get(f.name, default_str)

                raw_val = self.panel.text_field(
                    f"{self.key}.input_{f.name}",
                    self.c.x + 80,
                    self.c.y,
                    150,
                    str(cur_val if cur_val is not None else ""),
                )
                if raw_val is not None:
                    self.builder_params[f.name] = str(raw_val)

            self.c.y += 28

        # "+ Add Action" Button unter die Inputs
        self.c.save()
        self.c.x += 15
        self.c.y += 5
        self.draw_button("+ Add Action", self.on_add_action, options={"w": 110, "h": 22})
        self.c.load()

        self.c.y += 38

    def draw_staged_queue(self, bw: int):
        self.panel.label(self.c.x + 15, self.c.y, "STAGED ACTIONS", "caption")
        self.c.y += 18

        box_w = bw - 30
        box_h = 135

        # Sub-Container für die Queue-Elemente
        self.panel.fill_rect(self.c.x + 15, self.c.y, box_w, box_h, "#14151b")

        if not self.staged_actions:
            self.panel.draw_text(self.c.x + 30, self.c.y + 20, "(Queue empty - add actions above)", 11, "#6e6e6e")
        else:
            for i, act in enumerate(self.staged_actions[:5]):
                args = {k: v for k, v in act.items() if k != "action"}
                txt = f"{i + 1}. {act.get('action')} {args}"
                self.panel.draw_text(self.c.x + 25, self.c.y + 10 + (i * 22), txt, 10, "white")

        self.c.y += box_h + 10

        # Buttons in einer Zeile sauber aufgereiht
        self.c.set_origin("x")
        self.c.save()
        self.c.x += 15

        self.draw_button("Clear", self.on_clear_staged, options={"w": 65, "h": 24})
        self.c.x += 75
        self.draw_button("Save Routine", self.on_save_staged_routine, options={"w": 105, "h": 24})
        self.c.x += 115
        self.draw_button("Start Job Now", self.on_run_staged_now, options={"w": 110, "h": 24})

        self.c.load()

    # -------------------------------------------------------------
    # EVENT-HANDLER
    # -------------------------------------------------------------

    def on_cancel_job(self, _):
        if self.target:
            self.target.store.cancel_job()

    def on_load_routine(self, _):
        if not self.target or not self.selected_routine_name:
            return
        routine = self.target.routines.get(self.selected_routine_name)
        if routine:
            self.target.store.assign_job(
                actions=routine.get("actions", []),
                routine_name=self.selected_routine_name,
                loop=routine.get("loop", True),
            )

    def on_add_action(self, _):
        action_cls = MACHINE_ACTION_REGISTRY.get(self.selected_action_name)
        if not action_cls:
            return

        payload = {"action": self.selected_action_name}
        for f in fields(action_cls):
            if f.name == "action":
                continue
            payload[f.name] = self.builder_params.get(f.name, f.default if f.default is not f.default_factory else 0)

        self.staged_actions.append(payload)

    def on_clear_staged(self, _):
        self.staged_actions.clear()

    def on_save_staged_routine(self, _):
        if not self.target or not self.staged_actions:
            return
        routine_name = f"routine_{len(self.target.routines.all()) + 1}"
        self.target.routines.save(routine_name, self.staged_actions, loop=self.builder_loop)

    def on_run_staged_now(self, _):
        if not self.target or not self.staged_actions:
            return
        self.target.store.assign_job(
            actions=list(self.staged_actions),
            routine_name="Custom",
            loop=self.builder_loop,
        )
