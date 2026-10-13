from page_panel import PagePanel


class InventoryPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "inventory")

        self.inventory: Inventory = get_component("inventory")

    def render(self, **_):
        super().render(**_)
        self.c.save()

        self.c.y += 10
        self.c.x += 20

        for i, slot in enumerate(self.inventory.get_slots()):
            if i % 9 == 0 and i != 0:
                for x in range(9):
                    self.c.load()
                self.c.y += 60

            w = self.draw_inventory_slot(slot.slot, slot.id, slot.value, w=100, h=50, text_size="auto")
            self.c.x += w + 5

        for i in self.inventory.get_slots():
            self.c.load()
        # self.c.pop()

    def draw_inventory_slot(
        self,
        index: int,
        item_id: str,
        value: int,
        active: bool = False,
        click_fn: Callable = None,
        w: int | "auto" = 50,
        h: int = 55,
        text_size: int | "auto" = 11,
    ) -> int:
        # Hover listener
        hover: bool = False
        m = self.panel.mouse()
        if m.over and m.x > self.c.x and m.x < self.c.x + w and m.y > self.c.y and m.y < self.c.y + h:
            hover = True

        label = str(item_id) or "(empty)"

        # Resize text so it fits the button
        if text_size == "auto":
            # start at default, gradially lowering
            text_size = 13

            label_length = len(label) * ((text_size / 2) + 0.5)
            while w - label_length <= 10:
                text_size -= 1
                label_length = len(label) * ((text_size / 2) + 0.5)

        if w == "auto":
            label_length = len(label) * (text_size / 2)
            if w - label_length <= 5:
                w += label_length + 5 - w

        # Background
        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#31323e" if active else "#272933" if hover else "#1e1f27")

        # Border
        self.panel.fill_rect(self.c.x, self.c.y, w * 0.6, 2, "#823ab6")
        self.panel.fill_rect(self.c.x, self.c.y, 2, h * 0.2, "#823ab6")

        self.panel.fill_rect(self.c.x + w - (w * 0.6), self.c.y + h - 2, w * 0.6, 2, "#823ab6")
        self.panel.fill_rect(self.c.x + w - 2, self.c.y + h - (h * 0.2), 2, h * 0.2, "#823ab6")

        # Text: Index
        self.panel.draw_text(self.c.x + 6, self.c.y + 10, f"{index + 1}:", 10, "accent")

        # Text: Label
        self.panel.draw_text(self.c.x + (w / 2) - len(label) * (((text_size / 2) / 2) + 0.5), self.c.y + 22, f"{label}", text_size, "text-bright")

        # Icon
        if item_id and item_id in self.panel.icon_ids():
            self.panel.draw_icon(self.c.x + 3, self.c.y + h - 23, item_id, 25)

        # Text: Value
        self.panel.draw_text(self.c.x + w - (len(str(value)) * 8), self.c.y + h - 10, str(value), 11, "#a19e0e")

        # Click listener
        for c in self.click_list:
            if c.x > self.c.x and c.x < self.c.x + w and c.y > self.c.y and c.y < self.c.y + h:
                if click_fn:
                    click_fn(index=index, item_id=item_id, value=value)

        return w
