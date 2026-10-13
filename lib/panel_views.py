class PanelViews:
    def __init__(self, panel: Panel, title="Control"):
        self.panel: Panel = panel
        self.title = title
        self.views = {}
        self.current_view = None
        self.view_params = {}
        self.history = []

    
    def register_view(self, name, render_fn):
        self.views[name] = render_fn

    
    def navigate_to(self, view_name, params=None, add_to_history=True):
        if self.current_view and add_to_history:
            self.history.append((self.current_view, self.view_params))

        self.current_view = view_name
        self.view_params = params or {}
        self.render()

    
    def go_back(self):
        if not self.history:
            return
        prev_view, prev_params = self.history.pop()
        self.navigate_to(prev_view, prev_params, add_to_history=False)

    
    def render(self):
        self.panel.clear()

        # Header
        # self.panel.label(12, 22, self.title, "caption")

        y_offset = 10
        if self.history:
            # click = self.panel.button("back", 10, y_offset, 60, 25, "close")
            # if click:
            #     self.go_back()
            y_offset += 35

        render_fn = self.views[self.current_view]
        
        if render_fn:
            render_fn(self.panel, self.view_params, start_y=y_offset, navigator=self)
