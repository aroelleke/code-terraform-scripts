import math
from dataclasses import fields, is_dataclass
from machine_actions import MACHINE_ACTION_REGISTRY
from page_panel import PagePanel
from vehicle import VehicleController


class VehicleTaskBuilderPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")
        self.target: VehicleController
        self.parent = None

        self.selected_action: str = "target_set"
        self.params: dict = {}
        self.staged_actions: list[dict] = []
        self.selected_idx: int | None = None
        self.routine_name_input: str = "routine_1"
        self.loop_flag: bool = False
        self.feedback_msg: str | None = None
        self.coord_rev: int = 0
        self.scroll_offset: int = 0
        self.selected_target_poi: str = "(Custom Coords)"

    def prepare(self, target: VehicleController = None, **_):
        super().prepare(**_)
        self.target = target

    def render(self, **_):
        super().render(**_)
        if not self.target:
            return

        self.c.y += 12
        self.c.save(True)

        self.draw_action_configurator()

        self.c.load()
        self.c.x += 370
        self.c.save(True)

        self.draw_staged_queue()

        self.c.load()

    def get_known_targets_sorted(self) -> list[tuple[str, tuple[int, int], float]]:
        cur_x, cur_y = 0, 0
        if self.target and self.target.has_nav():
            pos = self.target.ref.nav.get_position()
            cur_x, cur_y = int(pos.x), int(pos.y)

        targets = []

        # 1. Outposts
        try:
            for o in self.target.outpost_network.outposts():
                c = o.coords()
                ox, oy = int(c[0]), int(c[1])
                dist = math.hypot(ox - cur_x, oy - cur_y)
                targets.append((f"Outpost: {o.name}", (ox, oy), dist))
        except Exception:
            pass

        # 2. Vehicles
        try:
            fleet = get_component("fleet")
            for v in fleet.vehicles():
                if v.id != self.target.ref.id:
                    try:
                        v_pos = v.nav.get_position()
                        vx, vy = int(v_pos.x), int(v_pos.y)
                        dist = math.hypot(vx - cur_x, vy - cur_y)
                        targets.append((f"Vehicle: {v.name}", (vx, vy), dist))
                    except Exception:
                        pass
        except Exception:
            pass

        # 3. POIs / Sites aus Journal & Nocturna
        try:
            journal = get_component("journal")
            poi_list = getattr(journal, "pois", None) or getattr(journal, "points_of_interest", None)
            if callable(poi_list):
                for p in poi_list():
                    px, py = int(p.x), int(p.y)
                    dist = math.hypot(px - cur_x, py - cur_y)
                    targets.append((f"POI: {p.name}", (px, py), dist))
        except Exception:
            pass

        try:
            planet = get_component("nocturna")
            if hasattr(planet, "sites"):
                for s in planet.sites():
                    sx, sy = int(s.x), int(s.y)
                    dist = math.hypot(sx - cur_x, sy - cur_y)
                    targets.append((f"Site: {s.name}", (sx, sy), dist))
        except Exception:
            pass

        # Nach Distanz sortieren
        targets.sort(key=lambda t: t[2])
        return targets

    def draw_action_configurator(self):
        w = 340
        h = 280

        self.panel.label(self.c.x + 12, self.c.y, "ACTION CONFIG", "caption")
        self.c.x += 10
        self.c.y += 15

        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#1e1f27")
        self.panel.draw_rect(self.c.x, self.c.y, 2, h, "accent")

        action_y = self.c.y + 12
        self.panel.draw_text(self.c.x + 15, action_y + 5, "Action:", 11, "accent")

        action_names = list(MACHINE_ACTION_REGISTRY.keys())
        chosen = self.panel.combo(
            f"{self.key}.action_sel",
            self.c.x + 75,
            action_y,
            200,
            action_names,
            self.selected_action,
            size=22,
        )
        if chosen and chosen != self.selected_action:
            self.selected_action = chosen
            self.params.clear()
            self.selected_target_poi = "(Custom Coords)"
            self.feedback_msg = None

        self.draw_smart_parameters(action_y + 34)

        btn_lbl = "✓ Update Action" if self.selected_idx is not None else "+ Add Action"
        self.c.save()
        self.c.x += 15
        self.c.y += h - 34
        self.draw_button(btn_lbl, self.on_save_action_param, options={"w": 120, "h": 22})

        if self.selected_idx is not None:
            self.c.x += 130
            self.draw_button("Cancel", self.on_cancel_edit, options={"w": 65, "h": 22})

        self.c.load()

    def draw_smart_parameters(self, start_y: int):
        action_cls = MACHINE_ACTION_REGISTRY.get(self.selected_action)
        if not action_cls or not is_dataclass(action_cls):
            return

        row = 0
        for f in fields(action_cls):
            if f.name == "action":
                continue

            field_y = start_y + (row * 32)
            lbl = f.name.replace("_", " ").capitalize()
            self.panel.draw_text(self.c.x + 15, field_y + 5, lbl, 11, "white")

            if f.name == "coords":
                coords = self.params.get("coords", (0, 0))
                rx = self.panel.text_field(f"{self.key}.cx_{self.coord_rev}", self.c.x + 75, field_y, 45, str(coords[0]))
                ry = self.panel.text_field(f"{self.key}.cy_{self.coord_rev}", self.c.x + 125, field_y, 45, str(coords[1]))

                # Button "Here" sauber ausgerichtet (Y+1 für perfekte Zentrierung, X+185)
                self.c.save()
                self.c.x += 185
                self.c.y = field_y + 1
                self.draw_button("Here", self.on_use_cur_pos, options={"w": 46, "h": 20})
                self.c.load()

                # Prüfen auf manuelle Eingabe -> Dropdown zurücksetzen
                new_x = int(rx) if rx and rx.lstrip("-").isdigit() else coords[0]
                new_y = int(ry) if ry and ry.lstrip("-").isdigit() else coords[1]
                if (new_x, new_y) != coords:
                    self.params["coords"] = (new_x, new_y)
                    self.selected_target_poi = "(Custom Coords)"

                # Target Selector (sortiert nach Distanz)
                row += 1
                poi_y = start_y + (row * 32)
                self.panel.draw_text(self.c.x + 15, poi_y + 5, "Target:", 11, "accent")

                sorted_targets = self.get_known_targets_sorted()
                target_labels = ["(Custom Coords)"] + [f"{t[0]} ({int(t[2])}m)" for t in sorted_targets]
                lookup = {f"{t[0]} ({int(t[2])}m)": t[1] for t in sorted_targets}

                chosen_poi = self.panel.combo(
                    f"{self.key}.target_picker",
                    self.c.x + 75,
                    poi_y,
                    200,
                    target_labels,
                    self.selected_target_poi,
                    size=22,
                )
                if chosen_poi and chosen_poi != self.selected_target_poi:
                    self.selected_target_poi = chosen_poi
                    if chosen_poi in lookup:
                        self.params["coords"] = lookup[chosen_poi]
                        self.coord_rev += 1

            elif f.name in ("station", "target_id"):
                outposts = [o.name for o in self.target.outpost_network.outposts()]
                cur = self.params.get(f.name, outposts[0] if outposts else "")
                selected = self.panel.combo(f"{self.key}.sel_station", self.c.x + 75, field_y, 180, outposts, cur, size=22)
                if selected:
                    self.params[f.name] = selected

            elif f.name == "module_slot":
                mods = [f"{m.index}: {m.module_id or 'empty'}" for m in self.target.ref.modules()]
                cur_str = mods[0] if mods else "0"
                sel_mod = self.panel.combo(f"{self.key}.sel_mod", self.c.x + 75, field_y, 180, mods, cur_str, size=22)
                if sel_mod:
                    self.params[f.name] = int(sel_mod.split(":")[0])

            elif f.name == "type":
                types = ["input", "output"]
                cur_t = self.params.get(f.name, "input")
                sel_t = self.panel.combo(f"{self.key}.sel_type", self.c.x + 75, field_y, 120, types, cur_t, size=22)
                if sel_t:
                    self.params[f.name] = sel_t

            elif f.name in ("duration", "count", "power", "internal_index", "rack_index"):
                val = self.params.get(f.name, 1)
                raw = self.panel.text_field(f"{self.key}.in_{f.name}", self.c.x + 75, field_y, 65, str(val))
                try:
                    self.params[f.name] = int(raw) if raw else val
                except (ValueError, TypeError):
                    pass

            else:
                val = self.params.get(f.name, "")
                raw = self.panel.text_field(f"{self.key}.in_{f.name}", self.c.x + 75, field_y, 180, str(val))
                if raw is not None:
                    self.params[f.name] = str(raw)

            row += 1

        if row == 0:
            self.panel.draw_text(self.c.x + 15, start_y + 10, "(No parameters required)", 11, "#6e6e6e")

    def draw_staged_queue(self):
        total_w = self.panel.width()
        w = max(380, total_w - self.c.x - 20)
        h = 280

        self.panel.label(self.c.x + 12, self.c.y, "STAGED ACTIONS", "caption")

        total_items = len(self.staged_actions)
        if total_items > 5:
            self.c.save()
            self.c.x = self.c.x + w - 46
            self.c.y -= 2
            self.draw_button("▲", self.on_scroll_up, disabled=(self.scroll_offset == 0), options={"w": 18, "h": 16})
            self.c.x += 22
            self.draw_button("▼", self.on_scroll_down, disabled=(self.scroll_offset + 5 >= total_items), options={"w": 18, "h": 16})
            self.c.load()

        self.c.x += 10
        self.c.y += 15

        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#1e1f27")
        self.panel.draw_rect(self.c.x, self.c.y, 2, h, "accent")

        box_y = self.c.y + 12
        box_h = 150
        self.panel.fill_rect(self.c.x + 15, box_y, w - 30, box_h, "#14151b")

        if not self.staged_actions:
            self.panel.draw_text(self.c.x + 30, box_y + 20, "(Queue empty - configure on the left)", 11, "#6e6e6e")
        else:
            visible_slice = self.staged_actions[self.scroll_offset : self.scroll_offset + 5]
            for visible_i, act in enumerate(visible_slice):
                real_i = self.scroll_offset + visible_i
                line_y = box_y + 8 + (visible_i * 28)
                is_sel = self.selected_idx == real_i
                args = {k: v for k, v in act.items() if k != "action"}

                if is_sel:
                    self.panel.fill_rect(self.c.x + 18, line_y - 2, w - 36, 25, "#282a36")

                self.panel.draw_text(self.c.x + 24, line_y + 4, f"{real_i + 1}:", 10, "success" if is_sel else "accent")
                self.panel.draw_text(self.c.x + 44, line_y + 4, act.get("action"), 11, "white")
                self.panel.draw_text(self.c.x + 135, line_y + 4, str(args), 10, "text-bright")

                # Kompakter Map-Style Button-Block (90px Abstand vom rechten Rand garantiert kein Überlappen)
                btn_base_x = self.c.x + w - 90
                self.c.save()

                # Geteilte Vertikale Box (genau wie Map Zoom)
                self.c.x = btn_base_x
                self.c.y = line_y
                # Up-Button oben
                self.draw_button("▲", lambda _, idx=real_i: self.on_move_up(idx), disabled=(real_i == 0), options={"w": 18, "h": 11})
                # Down-Button direkt darunter
                self.c.y = line_y + 11
                self.draw_button(
                    "▼", lambda _, idx=real_i: self.on_move_down(idx), disabled=(real_i >= len(self.staged_actions) - 1), options={"w": 18, "h": 11}
                )

                # Edit & Delete Buttons mit Map-Styling
                self.c.y = line_y
                self.c.x = btn_base_x + 24
                self.draw_button("E", lambda _, idx=real_i: self.on_select_for_edit(idx), options={"w": 20, "h": 22})

                self.c.x = btn_base_x + 48
                self.draw_button("✕", lambda _, idx=real_i: self.on_delete_action(idx), options={"w": 20, "h": 22})

                self.c.load()

        # Name & Loop-Switch (Loop standardmäßig False / AUS)
        ctrl_y = box_y + box_h + 10
        self.panel.draw_text(self.c.x + 15, ctrl_y + 4, "Name:", 11, "accent")
        raw_name = self.panel.text_field(f"{self.key}.routine_name", self.c.x + 60, ctrl_y, 140, self.routine_name_input)
        if raw_name:
            self.routine_name_input = raw_name

        self.panel.draw_text(self.c.x + 215, ctrl_y + 4, "Loop", 11, "accent")
        sw_val = self.panel.switch(f"{self.key}.builder_loop_sw", self.c.x + 250, ctrl_y + 1, self.loop_flag)
        if sw_val is not None:
            self.loop_flag = bool(sw_val)

        btn_y = ctrl_y + 32
        self.c.save()
        self.c.y = btn_y
        self.c.x += 15

        self.draw_button("Clear", self.on_clear, options={"w": 60, "h": 22})
        self.c.x += 70
        self.draw_button("Save Routine", self.on_save, options={"w": 100, "h": 22})
        self.c.x += 110
        self.draw_button("Start Now", self.on_start_now, options={"w": 85, "h": 22})

        if self.feedback_msg:
            self.c.x += 95
            self.panel.draw_text(self.c.x, btn_y + 4, self.feedback_msg, 11, "success")

        self.c.load()

    def on_scroll_up(self, _):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def on_scroll_down(self, _):
        if self.scroll_offset + 5 < len(self.staged_actions):
            self.scroll_offset += 1

    def on_use_cur_pos(self, _):
        if self.target and self.target.has_nav():
            pos = self.target.ref.nav.get_position()
            self.params["coords"] = (int(pos.x), int(pos.y))
            self.selected_target_poi = "(Custom Coords)"
            self.coord_rev += 1

    def on_save_action_param(self, _):
        action_cls = MACHINE_ACTION_REGISTRY.get(self.selected_action)
        if not action_cls:
            return

        payload = {"action": self.selected_action}
        for f in fields(action_cls):
            if f.name == "action":
                continue
            payload[f.name] = self.params.get(f.name, getattr(f, "default", None))

        if self.selected_idx is not None and self.selected_idx < len(self.staged_actions):
            self.staged_actions[self.selected_idx] = payload
            self.selected_idx = None
        else:
            self.staged_actions.append(payload)

        self.feedback_msg = None

    def on_cancel_edit(self, _):
        self.selected_idx = None
        self.params.clear()

    def on_select_for_edit(self, idx: int):
        self.selected_idx = idx
        act = self.staged_actions[idx]
        self.selected_action = act.get("action")
        self.params = {k: v for k, v in act.items() if k != "action"}
        self.selected_target_poi = "(Custom Coords)"
        self.coord_rev += 1

    def on_move_up(self, idx: int):
        if idx > 0:
            self.staged_actions[idx - 1], self.staged_actions[idx] = self.staged_actions[idx], self.staged_actions[idx - 1]
            if self.selected_idx == idx:
                self.selected_idx = idx - 1

    def on_move_down(self, idx: int):
        if idx < len(self.staged_actions) - 1:
            self.staged_actions[idx + 1], self.staged_actions[idx] = self.staged_actions[idx], self.staged_actions[idx + 1]
            if self.selected_idx == idx:
                self.selected_idx = idx + 1

    def on_delete_action(self, idx: int):
        del self.staged_actions[idx]
        if self.selected_idx == idx:
            self.selected_idx = None
            self.params.clear()
        elif self.selected_idx is not None and self.selected_idx > idx:
            self.selected_idx -= 1
        if self.scroll_offset > 0 and len(self.staged_actions) <= self.scroll_offset + 4:
            self.scroll_offset -= 1

    def on_clear(self, _):
        self.staged_actions.clear()
        self.selected_idx = None
        self.feedback_msg = None
        self.scroll_offset = 0

    def on_save(self, _):
        if not self.target or not self.staged_actions:
            return
        name = self.routine_name_input.strip() or "unnamed_routine"
        self.target.routines.save(name, self.staged_actions, loop=self.loop_flag)

        self.staged_actions = []
        self.selected_idx = None
        self.params.clear()
        self.routine_name_input = f"routine_{len(self.target.routines.all()) + 1}"
        self.loop_flag = False
        self.scroll_offset = 0
        self.selected_target_poi = "(Custom Coords)"
        self.feedback_msg = "Saved & Reset!"

    def on_start_now(self, _):
        if not self.target or not self.staged_actions:
            return
        self.target.store.assign_job(
            actions=list(self.staged_actions),
            routine_name="Custom",
            loop=self.loop_flag,
        )
        self.feedback_msg = "Started!"
