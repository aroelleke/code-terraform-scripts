from panel_views import PanelViews


panel_views = PanelViews(panel, "Biology Lab")

items = [
    get_component("bio_collector_1"),
    get_component("bio_lab_1"),
    get_component("bio_exchange_1")
]


def draw_default_page(panel, view_params, start_y, navigator):
    panel.label(12, 22, "Biology Lab", "caption")
    
    for i, item in enumerate(items):
        y = 50 * (i + 1)
        
        panel.status_dot(20, y, 5, "running")
        panel.draw_text(38, y, item.name, 13)
        
        clicked = panel.button(f"open.{item.name}", panel.width() - 70, y - 15, 50, 26, "view")

        if clicked:
            panel_views.navigate_to("detailed", { "id": item.id, "index": i })
            
        # Add a devider to every item but the last
        if i != len(items) - 1:
            divider_y = y + 23
            panel.divider(panel.width() * 0.05, divider_y, panel.width() * 0.95, divider_y)


def draw_detailed_page(panel, view_params, start_y, navigator):
    # Get item for ease of use
    item = items[view_params.index] 

    # CAPTION
    panel.label(12, 22, view_params["id"], "caption")

    # STATUS
    # panel.draw_text(20, 50, "Status", 13)
    # panel.status_dot(100, 50, 5, )
    # panel.draw_text(120, 50, item.status(), 13, "accent")
    
    # panel.draw_text(20, 70, "Battery", 13)
    # panel.progress_bar(92, 70 - 6, 80, 10, item.battery.level(), get_battery_color(item.battery.level()))
    # panel.draw_text(117, 70, f"{item.battery.level() * 100}%", 13, "black")
    
    panel.divider(panel.width() * 0.05, 50 + 20 * 3, panel.width() * 0.95, 50 + 20 * 3)

    # ACTIONS
    panel.label(12, 50 + 20 * 4, "ACTIONS", "caption")
    
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