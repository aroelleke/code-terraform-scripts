from helper import clamp, is_point_in_rect
from outpost import OutpostController
from page_panel import PagePanel


class OutpostBuildingsPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "outpost")

        self.target: OutpostController
        self.item_list: list[ShopItem] = []

        self.table_size = (3, 4)
        self.searchbar: str = ""
        self.page: int = 1
        self.page_count: int = 1

    def prepare(self, target: OutpostController = None, **_):
        super().prepare(**_)

        self.target = target
        self.update_item_list()

    def update_item_list(self):
        def check(item: BuildingRef):
            return not self.searchbar or (
                self.searchbar and (self.searchbar in item.name or self.searchbar in item.id or self.searchbar in item.type_id)
            )

        items_per_page = self.table_size[0] * self.table_size[1]
        self.item_list = [item for item in self.target.ref.buildings() if check(item)]

        total_pages = (len(self.item_list) + items_per_page - 1) // items_per_page
        self.page_count = max(1, total_pages)

    def render(self, **_):
        super().render(**_)

        self.c.save()

        self.panel.fill_rect(0, self.c.y, self.panel.width(), 2, "bg-surface")
        self.c.y += 2
        self.c.y += 3

        self.draw_searchbar()
        self.c.y += 22 + 3

        self.panel.fill_rect(0, self.c.y, self.panel.width(), 2, "bg-surface")
        self.c.y += 2

        self.c.save()
        self.draw_pagination()

        self.c.x = 0
        self.c.save(True)

        self.draw_building_list()

    def draw_searchbar(self):
        self.c.save()
        self.c.x += 5
        size = 22

        bg_color = "hsl(0, 0%, 17%)"
        border_color = "hsl(5, 80%, 67%)" if self.searchbar else "hsl(0, 0%, 50%)"

        self.panel.fill_rect(self.c.x, self.c.y, size, size, bg_color)
        self.panel.draw_rect(self.c.x, self.c.y, size, size, border_color)
        for c in self.click_list:
            if is_point_in_rect(c.x, c.y, self.c.x, self.c.y, self.c.x + size, self.c.y + size):
                self.panel.forget(f"{self.key}.searchbar")

        rect = (self.c.x + (size / 2), self.c.y + (size / 2))
        line1 = [rect[0] - (size / 4), rect[1] - (size / 4), rect[0] + (size / 4), rect[1] + (size / 4)]
        line2 = [rect[0] - (size / 4), rect[1] + (size / 4), rect[0] + (size / 4), rect[1] - (size / 4)]
        self.panel.draw_line(*line1, border_color, 2)
        self.panel.draw_line(*line2, border_color, 2)
        self.c.x += 25

        searchbar = self.panel.text_field(f"{self.key}.searchbar", self.c.x, self.c.y, 300, placeholder="Search here...", size=22)
        if self.searchbar != searchbar:
            self.searchbar = searchbar
            self.page = 1
        self.c.load()

    def draw_pagination(self):
        self.c.save()

        self.c.y = self.panel.height() - 25

        disabled = self.page_count < 2

        self.panel.draw_text(self.c.x + 6, self.c.y + 10, "Page:", 13, "#a9aab7")
        self.c.x += 50
        self.panel.draw_text(self.c.x + 6, self.c.y + 10, f"{self.page}", 13, "#ebebf7" if not disabled else "#a9aab7")
        self.c.x += 15
        self.panel.draw_text(self.c.x + 6, self.c.y + 10, f"/{self.page_count}", 13, "#a9aab7")
        self.c.x += 40

        width = self.draw_button("Prev", self.prev_page, disabled=disabled or self.page <= 1)
        self.c.x += width + 10

        width = self.draw_button("Next", self.next_page, disabled=disabled or self.page >= self.page_count)
        self.c.x += width + 20

        for i in range(self.page_count):
            width = self.draw_button(str(i + 1), lambda _: self.jump_to_page(i + 1), active=i + 1 == self.page, disabled=disabled)
            self.c.x += width + 5

        self.c.load()

    def next_page(self, _):
        self.page += 1 if self.page != self.page_count else 0

    def prev_page(self, _):
        self.page -= 1 if self.page != 1 else 0

    def jump_to_page(self, page):
        self.page = clamp(page, 0, self.page_count)

    def draw_building_list(self):
        items_per_page = self.table_size[0] * self.table_size[1]
        margin = (10, 10)
        space = 10
        pagination_height = 25

        item_size = (
            (self.panel.width() - (self.c.x + (space * (self.table_size[0] - 1)) + (margin[0] * 2))) / self.table_size[0],
            (self.panel.height() - (pagination_height + self.c.y + (space * (self.table_size[1] - 1)) + (margin[1]) * 2)) / self.table_size[1],
        )

        self.c.x = margin[0]
        self.c.y += margin[1]

        self.c.save(True)
        page = self.item_list[(self.page - 1) * items_per_page : self.page * items_per_page]
        for i, item in enumerate(page):
            x = i % self.table_size[0]
            y = i // self.table_size[0]

            self.c.x += (item_size[0] + space) * x
            self.c.y += (item_size[1] + space) * y

            self.draw_building(item, *item_size)

            self.c.reset_x()
            self.c.reset_y()

    def draw_building(self, building: BuildingRef, w: int, h: int):
        self.c.save()

        self.panel.fill_rect(self.c.x, self.c.y, w, h, "hsl(98, 10%, 25%)" if building.powered else "hsl(350, 10%, 25%)")
        self.panel.draw_rect(self.c.x, self.c.y, w, h, "hsl(98, 50%, 40%)" if building.powered else "hsl(350, 50%, 40%)")

        self.c.x += 10
        self.c.y += 11

        self.c.set_origin("x")

        self.panel.draw_text(self.c.x, self.c.y, "ID", 12, "accent")
        self.c.x += 40
        self.panel.draw_text(self.c.x, self.c.y, building.id, 12)

        self.c.reset_x()
        self.c.y += 12

        self.panel.draw_text(self.c.x, self.c.y, "Type", 12, "accent")
        self.c.x += 40
        self.panel.draw_text(self.c.x, self.c.y, building.type_id, 12)

        self.c.load()
