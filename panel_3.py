bio_exchange = get_component("bio_exchange_1")

while True:
    panel.clear()
    panel.label(12, 22, "Bio Lab", "caption")

    order = bio_exchange.active_order()
    
    panel.status_dot(20, 50, 5, "running" if order else "idle")
    panel.draw_text(38, 50, bio_exchange.name, 13)

    if order:
        panel.draw_text(200, 50, f"Current order: {order.name}", 13)

