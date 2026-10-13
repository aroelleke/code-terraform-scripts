from constants import VALID_MODULES_FOR_TYPE
from dataclasses_def import Position
from helper import is_point_in_rect
from page_panel import PagePanel
from vehicle import VehicleController


class VehicleModulesPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "vehicle")

        self.inventory: Inventory = get_component("inventory")

        self.target: VehicleController
        self.selected_module: MountSlot = None
        self.selected_slot: Slot = None

    def prepare(self, target: VehicleController = None, **_):
        super().prepare(**_)

        self.target = target
        if self.selected_module:
            self.selected_module = self.get_module(self.selected_module.index)
        if self.selected_slot:
            self.selected_slot = self.get_slot(self.selected_slot.slot)

    def render(self, **_):
        super().render(**_)

        self.c.y += 20
        self.c.save(True)

        self.draw_modules()
        self.draw_configure()

    def draw_modules(self):
        self.panel.label(self.c.x + 12, self.c.y, "MODULES", "caption")

        self.c.x += 20
        self.c.y += 10

        self.c.set_origin("y")

        columns = 1
        for i, module in enumerate(self.target.ref.modules()):
            w = self.draw_module_element(module)

            if i < len(self.target.ref.modules()) - 1:
                if (i + 1) % 4 == 0:
                    self.c.reset_y()
                    self.c.x += w + 10
                    columns += 1
                else:
                    self.c.y += 60

        self.c.load()

        self.c.x += (200 * columns) + 50
        self.c.save()

        if not self.target.is_home():
            return

    def draw_configure(self):
        self.panel.label(self.c.x + 12, self.c.y, "CONFIGURE", "caption")

        self.c.x += 20
        self.c.y += 10
        self.c.save(True)

        pos = self.target.ref.nav.get_position()
        if not self.target.has_nav() or (pos.x == 0 and pos.y == 0):
            mount_disabled = not self.selected_slot
            dismount_disabled = not self.selected_module or not self.selected_module.module_id

            self.draw_button("Mount", self.request_mount, disabled=mount_disabled, options={"w": 80})
            self.c.x += 90
            self.draw_button("Dismount", self.request_unmount, disabled=dismount_disabled, options={"w": 80})

            self.c.load()

            self.c.y += 50

            self.c.set_origin("x")
            slots: list[Slot] = self.get_slots()
            for i, slot in enumerate(slots):
                w = self.draw_inventory_slot(slot, w=100, h=50, text_size="auto")

                if (i + 1) % 4 == 0:
                    self.c.reset_x()
                    self.c.y += 60
                else:
                    self.c.x += w + 10
        else:
            self.c.y += 10
            self.panel.draw_text(self.c.x, self.c.y, "Move to home outpost to configure modules", 13, "warning")

    def select_slot(self, slot: Slot):
        if self.selected_slot and self.selected_slot.slot == slot.slot:
            self.selected_slot = None
        else:
            self.selected_slot = slot

    def draw_module_element(self, module: MountSlot) -> int:
        w, h = 200, 50

        active = self.selected_module and self.selected_module.index == module.index
        hover: bool = False
        if is_point_in_rect(self.mouse.x, self.mouse.y, self.c.x, self.c.y, self.c.x + w, self.c.y + h):
            hover = True

        label = str(module.module_id) or "(empty)"

        # Determine text size, starting at a default and lowering
        text_size = 12

        label_length = len(label) * ((text_size / 1.9) + 0.5)
        while w - label_length <= 10:
            text_size -= 1
            label_length = len(label) * ((text_size / 1.9) + 0.5)

        # Background
        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#31323e" if active else "#272933" if hover else "#1e1f27")

        if active:
            # Border
            self.panel.fill_rect(self.c.x, self.c.y, 4, h, "success" if module.module_id else "warning")
            self.panel.fill_rect(self.c.x + w - 30, self.c.y + h - 1, 30, 1, "success" if module.module_id else "warning")

            # Text: Index
            self.panel.draw_text(self.c.x + 6, self.c.y + 10, f"{module.index + 1}:", 12, "white")
        else:
            # Border
            self.panel.fill_rect(self.c.x, self.c.y, 2, h, "success" if module.module_id else "warning")

            # Text: Index
            self.panel.draw_text(self.c.x + 7, self.c.y + 10, f"{module.index + 1}:", 10, "accent")

        # Text: Label
        self.panel.draw_text(
            self.c.x + (w / 2) - len(label) * (((text_size / 2) / 2) + 0.5),
            self.c.y + 22,
            f"{module.module_id or '(empty)'}",
            text_size,
            "text-bright" if module.module_id else "warning",
        )

        # Icon
        if module.module_id:
            self.panel.draw_icon(self.c.x + 3, self.c.y + h - 23, module.module_id, 25)

        # Text: module type
        self.panel.draw_text(self.c.x + w - (len(module.type) * 7), self.c.y + h - 10, module.type, 11, "success" if module.module_id else "error")

        # Click listener
        for c in self.click_list:
            if c.x > self.c.x and c.x < self.c.x + w and c.y > self.c.y and c.y < self.c.y + h:
                self.selected_module = module

        return w

    def draw_inventory_slot(
        self,
        slot: Slot,
        w: int | "auto" = 50,
        h: int = 55,
        text_size: int | "auto" = 11,
    ) -> int:
        # Set active and disabled flags
        active = self.selected_slot and self.selected_slot.slot == slot.slot
        disabled = not self.selected_module or slot.id not in VALID_MODULES_FOR_TYPE[self.selected_module.type] or self.selected_module.module_id
        hover: bool = False
        if is_point_in_rect(self.mouse.x, self.mouse.y, self.c.x, self.c.y, self.c.x + w, self.c.y + h):
            if not disabled:
                hover = True

        label = str(slot.name) or "(empty)"

        # Resize text so it fits the button
        if text_size == "auto":
            # start at default, gradially lowering
            text_size = 10

            label_length = len(label) * ((text_size / 2) + 0.5)
            while w - label_length <= 10:
                text_size -= 1
                label_length = len(label) * ((text_size / 2) + 0.5)

        if w == "auto":
            label_length = len(label) * (text_size / 2)
            if w - label_length <= 5:
                w += label_length + 5 - w

        color = "white" if not disabled else "#6e6e6e"
        border_color = "#823ab6" if not disabled else "hsl(275, 0%, 47%)"
        border_width = 4 if active else 2

        # Background
        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#31323e" if active else "#272933" if hover else "#1e1f27")

        # Border
        self.panel.fill_rect(self.c.x, self.c.y, w * 0.6, border_width, border_color)
        self.panel.fill_rect(self.c.x, self.c.y, border_width, h * 0.2, border_color)
        self.panel.fill_rect(self.c.x + w - (w * 0.6), self.c.y + h - border_width, w * 0.6, border_width, border_color)
        self.panel.fill_rect(self.c.x + w - border_width, self.c.y + h - (h * 0.2), border_width, h * 0.2, border_color)

        # Text: Index
        self.panel.draw_text(self.c.x + 6, self.c.y + 10, f"{slot.slot}:", 10, "accent" if not disabled else "#6e6e6e")

        # Text: Label
        self.panel.draw_text(
            self.c.x + (w / 2) - len(label) * (((text_size / 2) / 2) + 0.5),
            self.c.y + 22,
            f"{label}",
            text_size,
            "text-bright" if not disabled else "#6e6e6e",
        )

        # Icon
        self.panel.draw_icon(self.c.x + 3, self.c.y + h - 23, slot.id, 25)

        # Text: Value
        self.panel.draw_text(
            self.c.x + w - (len(str(slot.value)) * 8), self.c.y + h - 10, str(slot.value), 11, "#a19e0e" if not disabled else "#6e6e6e"
        )

        if not disabled:
            for c in self.click_list:
                if is_point_in_rect(c.x, c.y, self.c.x, self.c.y, self.c.x + w, self.c.y + h):
                    self.select_slot(slot)

        return w

    def request_mount(self, _):
        if not self.selected_module or not self.selected_slot:
            return

        data = {
            "module_index": self.selected_module.index,
            "item_id": self.selected_slot.id,
        }
        self.target.comms.new("mount_module", data)

        self.selected_slot = None

    def request_unmount(self, _):
        if not self.selected_module:
            return

        data = {"module_index": self.selected_module.index}
        self.target.comms.new("unmount_module", data)

    def get_module(self, index: int):
        module = [item for item in self.target.ref.modules() if item.index == index]
        if module:
            return module[0]

    def get_slots(self) -> list[Slot]:
        return [slot for slot in self.inventory.get_slots() if slot.id in VALID_MODULES_FOR_TYPE["universal"]]

    def get_slot(self, index: int) -> Slot:
        slot = [item for item in self.inventory.get_slots() if item.slot == index]
        if slot:
            return slot[0]
