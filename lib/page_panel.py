from helper import safe_call_func
from panel_wrapper import PanelWrapper


class PagePanel(PanelWrapper):
    def __init__(self, panel: Panel, key: str, root: bool = False):
        super().__init__(panel, key)
        self.root = root

        self.panels: dict[str, PanelWrapper] = {}
        self.tabs: list[str] = []
        self.tab: str = ""

        self.show_config: bool = False

    def on_init(self):
        pass

    def on_destroy(self):
        if self.tabs:
            self.tab = self.tabs[0]

    def run(self):
        while self.root:
            self.render(x=5, y=5)

    def prepare(self, **_):
        if self.root:
            super().prepare(mouse=self.panel.mouse(), click_list=self.panel.clicks(), **_)
        else:
            super().prepare(**_)

        self.tabs: list[str] = self.panels.keys()

        if not self.tab or self.tab not in self.tabs:
            if self.tabs:
                self.tab = self.tabs[0]
            else:
                self.tab = None

    def render(self, **_):
        self.prepare(**_)

        # Prepare panel for next frame, only called at root panels to prevent conflicts
        if self.root:
            self.panel.clear()

        # Tabs
        if self.tabs:
            self.draw_tabs(True if self.root else False)
            self.c.y += 25 if not self.root else 30

        if self.root and self.tabs:
            self.panel.divider(0, self.c.y, self.panel.width(), self.c.y)
            self.c.y += 6

        self.c.save(True)

        panel = self.panels.get(self.tab)
        if panel:
            data = self.get_tab_data(self.tab)
            panel.render(x=self.c.x, y=self.c.y, mouse=self.mouse, click_list=self.click_list, **data)

        # if hasattr(self, "draw_config"):
        #     if self.show_config:
        #         self.draw_config()

    def get_tab_data(self, tab: str) -> dict:
        return {}

    def draw_tabs(self, big: bool = False):
        isize = 20
        options = {"h": isize, "text-size": 11}

        if big:
            isize += 5
            options = {"w": "auto", "h": isize, "text-size": 15}

        if self.has_config():
            if self.panel.icon_button(f"{self.key}.config", self.c.x, self.c.y, isize, "console"):
                if hasattr(self, "config"):
                    self.show_config = not self.show_config

        self.c.x += isize + 10

        for tab in self.tabs:
            width = self.draw_button(tab, self.set_tab, active=self.tab == tab, options=options)
            self.c.x += width + 7

        self.c.reset_x()

    def set_tab(self, value: str, **_):
        self._execute_lifecycle("destroy")
        self.tab = value
        self._execute_lifecycle("init")

    def _execute_lifecycle(self, type: literal["init", "destroy"]):
        page = self.panels.get(self.tab)
        if page:
            match type:
                case "init":
                    page.on_init()
                case "destroy":
                    page.on_destroy()

    def has_config(self) -> bool:
        return hasattr(self, "draw_config")
