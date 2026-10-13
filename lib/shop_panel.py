from constants import SHOP_ITEM_CATEGORIES
from helper import clamp, format_money, is_point_in_rect, text_dims
from page_panel import PagePanel


class ShopPanel(PagePanel):
    def __init__(self, panel: Panel):
        super().__init__(panel, "shop")
        self.commander: Commander = get_component("commander")
        self.shop: Shop = get_component("shop")

        # TODO: Rethink with RootPanel logic
        self.category_list: list[str] = SHOP_ITEM_CATEGORIES.keys()
        self.category: str = self.category_list[0]

        self.searchbar: str = ""
        self.page: int = 1
        self.page_count: int = 1
        self.selected_item: ShopItems = None
        self.selected_amount: int = 1

        self.credits: int = 0
        self.shop_size: tuple[int, int] = (4, 6)
        self.item_list: list[ShopItem] = []

    def prepare(self, **_):
        super().prepare(**_)
        self.credits = self.commander.get_credits()

        self.update_item_list()

    def update_item_list(self):
        def check(item: ShopItem):
            return (
                item.name in SHOP_ITEM_CATEGORIES[self.category]
                and not self.searchbar
                or (self.searchbar and (self.searchbar in item.name or self.searchbar in item.id))
            )

        items_per_page = self.shop_size[0] * self.shop_size[1]
        self.item_list = [item for item in self.shop.get_catalogue() if check(item)]

        total_pages = (len(self.item_list) + items_per_page - 1) // items_per_page
        self.set_page_count(max(1, total_pages))
        # self.set_page_count((len(self.item_list) // items_per_page))

    def render(self, **_):
        super().render(**_)

        self.draw_categories()

        self.panel.fill_rect(0, self.c.y, self.panel.width(), 2, "bg-surface")
        self.c.y += 2

        self.c.save(True)
        cart_w = 200
        self.draw_cart(cart_w)

        self.c.load()
        self.c.y += 3

        self.draw_searchbar()
        self.draw_item_count()
        self.draw_credits_display()

        self.c.y += 22 + 3

        self.panel.fill_rect(0, self.c.y, self.panel.width() - 200, 2, "bg-surface")
        self.c.y += 2

        self.c.save()
        self.draw_pagination()

        self.c.x = 0
        self.c.save(True)

        self.draw_shop(cart_w)

    def draw_categories(self):
        self.c.save()

        self.panel.draw_text(self.c.x, self.c.y + 10, "Categories", 13, "white")
        self.c.x += 90

        for category in self.category_list:
            width = self.draw_button(category, self.set_category, active=self.category == category, options={"h": 20, "text-size": 11})
            self.c.x += width + 5

        self.c.load()
        self.c.y += 25
        self.c.save(True)

    def set_category(self, value: str):
        self.category = value
        self.page = 1

    def draw_cart(self, w: int):
        # self.c.save()

        h = self.panel.height() - self.c.y
        start_w = self.panel.width() - w

        self.c.x = start_w
        self.c.save(True)

        # self.panel.fill_rect(self.c.x, self.c.y, w, h, "#2a2b37")
        self.panel.fill_rect(self.c.x, self.c.y, w, h, "bg-panel")
        self.panel.fill_rect(self.c.x, self.c.y, 4, h, "border")

        self.c.y += 10
        self.c.save(True)

        # Icon
        icon_size = 100
        self.c.x += (w / 2) - (icon_size / 2)

        self.panel.fill_rect(self.c.x, self.c.y, icon_size, icon_size, "bg-base")
        self.panel.draw_rect(self.c.x, self.c.y, icon_size, icon_size, "border")
        if self.selected_item:
            self.panel.draw_icon(self.c.x, self.c.y, self.selected_item.id, icon_size)

        self.c.load()

        self.c.x += 10
        self.c.y += icon_size + 20

        # Text: Name
        self.panel.draw_text(self.c.x, self.c.y, "NAME", 11, "text-muted", 50)
        self.c.y += 15

        # Setup words array
        words = []
        if self.selected_item:
            words = self.selected_item.name.split(" ")

        for i in range(3):
            line = ""

            while words and (len(line + words[0]) * ((13 / 2) + 0.5)) < (w - 20):
                if line:
                    line += " "
                line += words.pop(0)

            self.panel.draw_text(self.c.x, self.c.y, line, 13, "white")
            self.c.y += 12

        self.c.y += 20

        # Text: Cost
        self.panel.draw_text(self.c.x, self.c.y, "COST", 11, "text-muted", 50)
        self.c.y += 15
        if self.selected_item:
            self.panel.draw_text(self.c.x, self.c.y, format_money(self.selected_item.cost), 13, "white")

        self.c.y = self.panel.height() - 50
        total_cost = 0
        if self.selected_item:
            total_cost = self.selected_item.cost * int(self.selected_amount)

        total_cost_color = (
            "white" if not total_cost else "error" if self.credits < total_cost else "warning" if self.credits * 0.75 <= total_cost else "success"
        )
        self.panel.draw_text(self.c.x, self.c.y, "Total:", 13, "#a9aab7")
        self.panel.draw_text(self.c.x + 50, self.c.y, format_money(total_cost), 13, total_cost_color)

        self.c.y += 12

        self.selected_amount = self.panel.text_field("shop.amount", self.c.x, self.c.y - 2, 45, "1", size=25)
        self.c.x += 47
        self.panel.draw_text(self.c.x, self.c.y + 10, "x", 13, "white")
        self.c.x += 15
        self.draw_button("Buy", lambda _: self.buy(), active=False, disabled=not self.selected_item or self.credits < total_cost, options={"w": 65})

        self.c.load()

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
                self.panel.forget("shop.searchbar")

        rect = (self.c.x + (size / 2), self.c.y + (size / 2))
        line1 = [rect[0] - (size / 4), rect[1] - (size / 4), rect[0] + (size / 4), rect[1] + (size / 4)]
        line2 = [rect[0] - (size / 4), rect[1] + (size / 4), rect[0] + (size / 4), rect[1] - (size / 4)]
        self.panel.draw_line(*line1, border_color, 2)
        self.panel.draw_line(*line2, border_color, 2)
        self.c.x += 25

        searchbar = self.panel.text_field("shop.searchbar", self.c.x, self.c.y, 300, placeholder="Search here...", size=22)
        if self.searchbar != searchbar:
            self.searchbar = searchbar
            self.page = 1
        self.c.load()

    def draw_item_count(self):
        self.c.save()

        self.c.x += 300 + 25 + 10
        self.panel.draw_text(self.c.x, self.c.y + 11, "Items:", 14, "#c8c9d0")
        self.c.x += 55
        self.panel.draw_text(self.c.x, self.c.y + 11, f"{len(self.item_list)}", 14, "white")

        self.c.load()

    def draw_credits_display(self):
        self.c.save()

        label = format_money(self.credits)

        self.c.x += self.panel.width() - (200 + text_dims(label, 14)[0] + 15)
        # self.panel.draw_text(self.c.x, self.c.y + 11, "Credits:", 14, "#c8c9d0")

        self.panel.draw_text(self.c.x, self.c.y + 11, label, 14, "success" if self.credits > 0 else "error")

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

        width = self.draw_button("Prev", lambda *_: self.prev_page(), disabled=disabled or self.page <= 1)
        self.c.x += width + 10

        width = self.draw_button("Next", lambda *_: self.next_page(), disabled=disabled or self.page >= self.page_count)
        self.c.x += width + 20

        for i in range(self.page_count):
            width = self.draw_button(str(i + 1), lambda *_: self.jump_to_page(i + 1), active=i + 1 == self.page, disabled=disabled)
            self.c.x += width + 5

        self.c.load()

    def draw_shop(self, cart_w: int):
        margin = (10, 10)
        space = 5
        pagination_height = 25

        shop_item = (
            (self.panel.width() - (self.c.x + cart_w + (space * (self.shop_size[0] - 1)) + (margin[0] * 2))) / self.shop_size[0],
            (self.panel.height() - (self.c.y + pagination_height + (space * (self.shop_size[1] - 1)) + (margin[1] * 2))) / self.shop_size[1],
        )

        self.c.x = margin[0]
        self.c.y += margin[1]

        self.draw_shop_items(*shop_item, space)

    def draw_shop_items(self, w: int, h: int, space: int):
        items_per_page = self.shop_size[0] * self.shop_size[1]

        self.c.save(True)

        page = self.item_list[(self.page - 1) * items_per_page : self.page * items_per_page]
        for i, item in enumerate(page):
            x = i % self.shop_size[0]
            y = i // self.shop_size[0]

            self.c.x += (w + space) * x
            self.c.y += (h + space) * y

            self.draw_shop_item(i + ((self.page - 1) * items_per_page), item, click_fn=self.select_item, w=w, h=h, text_size="auto")

            self.c.reset_x()
            self.c.reset_y()

    def draw_shop_item(
        self,
        index: int,
        item: ShopItem,
        click_fn: Callable = None,
        w: int | "auto" = 50,
        h: int = 55,
        text_size: int | "auto" = 11,
    ) -> int:
        active = self.selected_item and self.selected_item.id == item.id
        can_buy = self.can_buy(item.cost)

        # Hover listener
        hover: bool = False
        m = self.panel.mouse()
        if m.over and m.x > self.c.x and m.x < self.c.x + w and m.y > self.c.y and m.y < self.c.y + h:
            hover = True

        label = str(item.name) or "(empty)"

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

        border_color = "#3ab63a" if can_buy else "#cf3131"

        # Background
        self.panel.fill_rect(self.c.x, self.c.y, w, h, "#31323e" if active else "#272933" if hover else "#1e1f27")

        # Border
        self.panel.fill_rect(self.c.x, self.c.y, w * 0.6, 2, border_color)
        self.panel.fill_rect(self.c.x, self.c.y, 2, h * 0.2, border_color)

        self.panel.fill_rect(self.c.x + w - (w * 0.6), self.c.y + h - 2, w * 0.6, 2, border_color)
        self.panel.fill_rect(self.c.x + w - 2, self.c.y + h - (h * 0.2), 2, h * 0.2, border_color)

        # Text: Index
        self.panel.draw_text(self.c.x + 6, self.c.y + 10, f"{index + 1}:", 10, "accent")

        # Text: Label
        self.c.save()

        words = label.split(" ")
        lines = []
        while words:
            line = ""

            while words and (len(line + words[0]) * ((text_size / 2) + 0.5)) < (w * 0.7):
                if line:
                    line += " "
                line += words.pop(0)

            lines.append(line)

        self.c.y += (15 + h) / 2 - (12 * len(lines)) // 2

        for line in lines:
            self.panel.draw_text(self.c.x + (w / 2) - len(line) * (((text_size / 2) / 2) + 0.5), self.c.y, f"{line}", text_size, "text-bright")
            self.c.y += 12

        self.c.load()

        # Icon
        if item.id and item.id in self.panel.icon_ids():
            self.panel.draw_icon(self.c.x + 3, self.c.y + h - 23, item.id, 25)

        # Text: Cost
        cost = format_money(item.cost)
        self.panel.draw_text(self.c.x + w - (len(cost) * ((11 / 2) + 2)), self.c.y + h - 10, cost, 11, border_color)

        # Click listener
        for c in self.click_list:
            if c.x > self.c.x and c.x < self.c.x + w and c.y > self.c.y and c.y < self.c.y + h:
                if click_fn:
                    click_fn(item)

        return w

    def set_page_count(self, count):
        self.page_count = count

    def next_page(self):
        self.page += 1 if self.page != self.page_count else 0

    def prev_page(self):
        self.page -= 1 if self.page != 1 else 0

    def jump_to_page(self, page):
        self.page = clamp(page, 0, self.page_count)

    def can_buy(self, cost: int):
        return self.credits >= cost

    def select_item(self, item: ShopItem):
        self.selected_item = item
        self.selected_amount = 1

    def buy(self):
        item = [item.id for item in self.shop.get_catalogue() if item.name == self.selected_item.name]
        if item:
            self.shop.buy(item[0], int(self.selected_amount))
            self.panel.set_text("shop.amount", "1")
