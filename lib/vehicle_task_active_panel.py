from page_panel import PagePanel
from vehicle import VehicleController


class VehicleTaskActivePanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")
        self.target: VehicleController
        self.parent = None

    def prepare(self, target: VehicleController = None, **_):
        super().prepare(**_)
        self.target = target
        if self.target:
            self.target.store.refresh()

    def render(self, **_):
        super().render(**_)
        if not self.target:
            return

        self.c.y += 12
        self.c.save(True)

        self.draw_active_job()

        self.c.load()
        self.c.x += 370
        self.c.save(True)

        self.draw_routine_presets()

        self.c.load()

    def draw_active_job(self):
        w = 340
        h = 280

        self.panel.label(self.c.x + 12, self.c.y, "CURRENT JOB", "caption")
        self.c.x += 10
        self.c.y += 15

        job = self.target.store.job

        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#1e1f27")
        self.panel.draw_rect(self.c.x, self.c.y, 2, h, "accent" if job else "#40424f")

        if not job:
            self.panel.fill_rect(self.c.x + 15, self.c.y + 15, w - 30, 45, "#14151b")
            self.panel.draw_text(self.c.x + 25, self.c.y + 26, "STATUS", 10, "accent")
            self.panel.draw_text(self.c.x + 85, self.c.y + 26, "IDLE", 12, "warning")
            self.panel.draw_text(self.c.x + 25, self.c.y + 90, "No active job assigned to this vehicle.", 11, "#6e6e6e")
            self.panel.draw_text(self.c.x + 25, self.c.y + 110, "Start a saved routine on the right or", 11, "#6e6e6e")
            self.panel.draw_text(self.c.x + 25, self.c.y + 130, "switch to 'Builder' to compose tasks.", 11, "#6e6e6e")
            return

        name = job.get("routine_name") or "Custom Task"
        step_idx = job.get("step_index", 0)
        actions = job.get("actions", [])
        loop = bool(job.get("loop", False))

        # Status Header Box
        self.panel.fill_rect(self.c.x + 15, self.c.y + 12, w - 30, 50, "#14151b")

        self.panel.draw_text(self.c.x + 25, self.c.y + 20, "Routine:", 11, "accent")
        self.panel.draw_text(self.c.x + 80, self.c.y + 20, name, 12, "white")

        self.panel.draw_text(self.c.x + 25, self.c.y + 38, "Progress:", 11, "accent")
        progress = (step_idx + 1) / len(actions) if actions else 0
        self.panel.progress_bar(self.c.x + 80, self.c.y + 37, 130, 13, progress, "success")
        self.panel.draw_text(self.c.x + 218, self.c.y + 38, f"{step_idx + 1}/{len(actions)}", 11, "text-bright")

        self.panel.draw_text(self.c.x + 265, self.c.y + 18, "Loop", 10, "accent")
        new_loop = self.panel.switch(f"{self.key}.live_loop", self.c.x + 265, self.c.y + 30, loop)
        if new_loop is not None and new_loop != loop:
            job["loop"] = new_loop
            raw = self.target.store.notebook.get(self.target.store.key, {})
            if isinstance(raw, dict):
                raw["job"] = job
                self.target.store.notebook.set(self.target.store.key, raw)

        # Steps Timeline mit bündigem Highlight
        box_y = self.c.y + 70
        box_h = 135
        self.panel.fill_rect(self.c.x + 15, box_y, w - 30, box_h, "#14151b")

        for i, act in enumerate(actions[:5]):
            y_pos = box_y + 8 + (i * 24)
            is_active = i == step_idx
            is_done = i < step_idx

            # Volle Kartenbreite für das Highlight inklusive Akzent-Kante
            if is_active:
                self.panel.fill_rect(self.c.x + 15, y_pos - 2, w - 30, 22, "#242533")
                self.panel.fill_rect(self.c.x + 15, y_pos - 2, 3, 22, "accent")

            color = "success" if is_active else "#6e6e6e" if is_done else "white"
            prefix = "▶" if is_active else "✓" if is_done else "•"
            lbl = f"{prefix} [{i + 1}] {act.get('action')}"
            self.panel.draw_text(self.c.x + 24, y_pos + 2, lbl, 11, color)

            args = {k: v for k, v in act.items() if k != "action"}
            if args:
                self.panel.draw_text(self.c.x + 130, y_pos + 2, str(args), 10, "text-bright" if is_active else "#555")

        self.c.save()
        self.c.x += 15
        self.c.y = self.c.y + h - 34
        self.draw_button("Abort Job", self.on_cancel, options={"w": 95, "h": 22})
        self.c.load()

    def draw_routine_presets(self):
        total_w = self.panel.width()
        w = max(380, total_w - self.c.x - 20)
        h = 280

        self.panel.label(self.c.x + 12, self.c.y, "SAVED ROUTINES", "caption")
        self.c.x += 10
        self.c.y += 15

        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#1e1f27")
        self.panel.draw_rect(self.c.x, self.c.y, 2, h, "accent")

        routines = self.target.routines.all()
        r_names = list(routines.keys())

        if not r_names:
            self.panel.draw_text(self.c.x + 20, self.c.y + 20, "No routines saved yet", 11, "#6e6e6e")
            return

        for i, name in enumerate(r_names[:4]):
            card_y = self.c.y + 14 + (i * 54)
            raw_entry = routines[name]

            if isinstance(raw_entry, dict):
                actions = raw_entry.get("actions", [])
                loop_val = raw_entry.get("loop", False)
            elif isinstance(raw_entry, list):
                actions = raw_entry
                loop_val = True
            else:
                actions = []
                loop_val = False

            loop_state = "Loop" if loop_val else "Once"
            act_count = len(actions)

            self.panel.fill_rect(self.c.x + 15, card_y, w - 30, 46, "#14151b")
            self.panel.draw_text(self.c.x + 25, card_y + 9, str(name), 12, "white")
            self.panel.draw_text(self.c.x + 25, card_y + 27, f"{act_count} steps • {loop_state}", 10, "accent")

            btn_y = card_y + 11
            self.c.save()
            self.c.y = btn_y

            self.c.x = self.c.x + w - 185
            self.draw_button("Start", lambda _, n=name: self.on_start_routine(n), options={"w": 50, "h": 22})

            self.c.x += 55
            self.draw_button("Edit", lambda _, n=name: self.on_edit_routine(n), options={"w": 45, "h": 22})

            self.c.x += 50
            self.draw_button("Del", lambda _, n=name: self.on_delete_routine(n), options={"w": 40, "h": 22})

            self.c.load()

    def on_cancel(self, _):
        if self.target:
            self.target.store.cancel_job()

    def on_start_routine(self, name: str):
        routine = self.target.routines.get(name)
        if not routine:
            return

        actions = routine.get("actions", []) if isinstance(routine, dict) else (routine if isinstance(routine, list) else [])
        loop = routine.get("loop", False) if isinstance(routine, dict) else True

        self.target.store.assign_job(
            actions=actions,
            routine_name=name,
            loop=loop,
        )

    def on_edit_routine(self, name: str):
        routine = self.target.routines.get(name)
        if not routine:
            return

        actions = routine.get("actions", []) if isinstance(routine, dict) else (routine if isinstance(routine, list) else [])
        loop = routine.get("loop", False) if isinstance(routine, dict) else True

        builder = None
        if hasattr(self, "parent") and self.parent and hasattr(self.parent, "panels"):
            builder = self.parent.panels.get("Builder")
            self.parent.set_tab("Builder")

        if builder:
            builder.staged_actions = [dict(a) for a in actions]
            builder.routine_name_input = name
            builder.loop_flag = loop
            builder.selected_idx = None
            builder.scroll_offset = 0

    def on_delete_routine(self, name: str):
        self.target.routines.delete(name)
