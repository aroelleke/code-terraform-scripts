from layout_cursor import LayoutCursor
from config_database import Config


class PanelBase:
    def __init__(self, panel: Panel):
        self.panel: Panel = panel
        self.c: LayoutCursor
        self.config: Config
        self.current_view: str

    def run(self):
        while True:
            self.reset_cursor()
            self.panel.clear()

            self.render()

    def reset_cursor(self):
        self.c = LayoutCursor(10, 5, 30)

    def render(self):
        raise NotImplementedError("Please Implement this method 'render'!")

    def draw_table(
        self,
        columns: List[Column],
        rows: List[Any],
        row_height: number = 27,
        is_selected_fn=None,
        on_render_row=None,
        selected_color_fill="#192119",
        selected_color_border="#1a3917",
    ):
        # Draw header
        header_y = self.c.y
        for col in columns:
            col_x = self.c.x + col.x if col.x >= 0 else self.panel.width() + col.x
            self.panel.draw_text(col_x, header_y, col.title, 13, "accent")

        self.c.next(row_height)

        # Draw rows
        for i, item in enumerate(rows):
            row_y = self.c.y

            # Highlight row
            if is_selected_fn and is_selected_fn(item):
                self.panel.fill_rect(7, row_y - 14, self.panel.width() - 14, row_height, selected_color_fill)
                self.panel.draw_rect(7, row_y - 14, self.panel.width() - 14, row_height, selected_color_border)

            # Draw content
            for col in columns:
                col_x = self.c.x + col.x if col.x >= 0 else self.panel.width() + col.x
                if col.render_fn:
                    col.render_fn(self.panel, col_x, row_y, item)

            self.c.next(row_height)

    def draw_battery(self, x, y, w, h, level: number, text_color: str = "black"):
        color = "success" if level > 0.5 else "warn" if level > 0.2 else "error"
        text = f"{int(level * 100)}%"

        self.panel.progress_bar(x, y - 8, w, h, level, color)
        self.panel.draw_text(x + 15, y, text, 13, text_color)

    def draw_power_gain(self, x, y, value: number):
        value = int(value)

        text = f"{'+' if value > 0 else ''}{value}W"
        color = "success" if value > 0 else "" if value == 0 else "error"

        self.panel.draw_text(x, y, text, 13, color)

    def draw_status_dot(self, x, y, color: str):
        self.panel.status_dot(x + 25, y, 5, color)

    def draw_building_count(self, x, y, ref):
        used = ref.buildings_used()
        cap = ref.buildings_capacity()
        free = cap - used
        color = "success" if free > 5 else "warning" if free > 0 else "error"
        self.panel.draw_text(x, y, f"{used}/{cap}", 13, color)

    def is_selected(self, id, type):
        pass

    def select_item(self, id: str, type: str):
        selection: dic = self.config.get("selection")
        selection[type] = id
        self.config.set("selection", selection)

    def draw_select_button(self, x, y, id, type):
        if not self.is_selected(id, type):
            if self.panel.button(f"select.{type}.{id}", x, y - 10, 50, 20, "select"):
                self.select_item(id, type)


class TableColumn:
    def __init__(self, key: str, type: str, header: str, x_offset: number):
        self.key: str = key
        self.type: str = type
        self.header: str = header
        self.x_offset: number = x_offset

        self.values: List = []


class Column:
    def __init__(
        self,
        title: str,
        x: number,
        width: number = 0,
        align: str = "left",
        render_fn=None,
    ):
        self.title = title
        self.x = x
        self.width = width
        self.render_fn = render_fn
