class PanelController:
    def __init__(self, panel: Panel):
        self.panel: Panel = panel
        self.pages: List[PanelPage] = []
        self.current_page: PanelPage | None = None
        self.state = {}
        self.history = []

        

        self.register_views()

    def register_views(self):
        raise NotImplementedError("Please Implement this method")

    def run(self):
        while True:
            self.render()

    def register_view(self, name, render_fn):
        view: PanelPage = PanelPage(name, render_fn)
        self.pages.append(view)

    def navigate_to(self, name):
        page = self.get_page(name)
        if not page:
            raise ValueError(f'No page with name "{name}" is registered!')

        self.current_page = page

    def render(self):
        self.panel.clear()

        self.pre_render()

        if self.current_page:
            if self.current_page.render:
                self.current_page.render(self.panel)

        self.post_render()

    def pre_render(self):
        pass

    def post_render(self):
        pass

    def get_page(self, name: str) -> PanelPage | None:
        pages = [page for page in self.pages if page.name == name]

        if len(pages) > 0:
            return pages[0]

    def draw_key_value(panel: Panel, cursor, label, value, val_color="text-value", key_w=80, size=13):
        cursor.down()
        panel.draw_text(cursor.x, cursor.y, label, size, "accent")
        panel.draw_text(cursor.x + key_w, cursor.y, str(value), size, val_color)


class PanelPage:
    def __init__(self, name: str, render_fn):
        self.name: str = name
        self.render = render_fn
