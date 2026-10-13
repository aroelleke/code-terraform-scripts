from panel_views import PanelViews


panel_views = PanelViews(panel, "Charging Stations")

items = [
    get_component("charging_station_1")
]


def draw_default_page(panel, view_params, start_y, navigator):
    for i, item in enumerate(items):
        y = 50 * (i + 1)
        
        panel.status_dot(20, y, 5, "running")
        panel.draw_text(38, y, item.name, 13)
        
        clicked = panel.button(f"open.{item.name}", panel.width() - 70, y - 15, 50, 26, "view")

        if clicked:
            panel_views.navigate_to("detailed", { "id": item.id })
            
        # Add a devider to every item but the last
        if i != len(items) - 1:
            divider_y = y + 23
            panel.divider(panel.width() * 0.05, divider_y, panel.width() * 0.95, divider_y)


def draw_detailed_page(panel, view_params, start_y, navigator):
    clicked = panel.button(f"close.{view_params["id"]}", panel.width() - 70, 10, 50, 26, "close")

    if clicked:
        panel_views.navigate_to("base", {})


def main():
    panel_views.register_view("base", draw_default_page)
    panel_views.register_view("detailed", draw_detailed_page)

    panel_views.navigate_to("base")

    while True:
        panel_views.render()


main()