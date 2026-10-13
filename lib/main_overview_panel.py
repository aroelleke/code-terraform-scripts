from panel import TableColumn, Column
from main_panel import MainPanel
from rover import RoverController
from pioneer import PioneerController
from outpost import OutpostController
from config_database import Config
from constants import VIEWS


class MainOverviewPanelController(MainPanel):
    def __init__(self, panel: Panel):
        super().__init__(panel)

        self.vehicle_list: dict[str, VehicleController] = {}
        self.outpost_list: dict[str, OutpostController] = {}

    def update_outposts(self):
        outposts = [item.id for item in self.outpost_network.outposts()]

        # Clean list of dead entries
        self.outpost_list = {id: item for id, item in self.outpost_list.items() if id in outposts}

        # Add new
        for id in outposts:
            if id not in self.outpost_list:
                self.outpost_list[id] = OutpostController(get_component(id))

    def update_vehicles(self):
        vehicles = [item.id for item in self.fleet.vehicles()]

        # Clean list of dead entries
        self.vehicle_list = {id: item for id, item in self.vehicle_list.items() if id in vehicles}

        # Add new
        for id in vehicles:
            if id not in self.vehicle_list:
                component = get_component(id)

                match component.type_id:
                    case "rover":
                        self.vehicle_list[id] = RoverController(component)
                    case "pioneer":
                        self.vehicle_list[id] = PioneerController(component)

    def render(self):
        self.update_outposts()
        self.update_vehicles()

        self.draw_header()
        self.handle_sync()

        match self.current_view:
            case "outpost":
                self.draw_outpost_list()
            case "vehicle":
                self.draw_vehicle_list()
            case "charging_station":
                pass
            case "grid":
                pass

        if self.show_config:
            self.draw_config()

    def draw_header(self):
        if self.panel.icon_button("header.config", self.c.x, self.c.y, 30, "console"):
            self.show_config = not self.show_config

        self.c.column(40)

        self.panel.label(self.c.x + 10, self.c.y + 15, "OVERVIEW", "title", "accent")

        self.c.pop()
        self.c.column(self.panel.width() - 200)

        selection = self.panel.combo(
            "header.select-type",
            self.c.x,
            self.c.y,
            175,
            VIEWS.keys(),
            VIEWS.keys()[0],
            # "Select Type",
            size=25,
        )
        if VIEWS[selection] != self.current_view:
            self.current_view = VIEWS[selection]

        self.c.pop()

        self.c.next(40)
        self.panel.divider(40, self.c.y, self.panel.width() - 40, self.c.y)
        self.c.next()

    def draw_config(self):
        self.c.reset()
        self.c.next(40)
        self.panel.card(self.c.x, self.c.y, 300, 150, "CONFIG")

        self.c.column(10)
        self.c.next()

    def draw_outpost_list(self):
        columns = [
            Column(
                "Power",
                0,
                render_fn=lambda p, x, y, item: self.draw_battery(x, y, 60, 15, item.grid.stored / item.grid.capacity),
            ),
            Column(
                "+/-",
                65,
                render_fn=lambda p, x, y, item: self.draw_power_gain(x, y, item.grid.net),
            ),
            Column(
                "Name",
                115,
                render_fn=lambda p, x, y, item: p.draw_text(x, y, item.ref.name(), 13),
            ),
            Column(
                "Builds",
                260,
                render_fn=lambda p, x, y, item: self.draw_building_count(x, y, item.ref),
            ),
            Column(
                "Coords",
                320,
                render_fn=lambda p, x, y, item: p.draw_text(x, y, f"{item.ref.coords()[0]},{item.ref.coords()[1]}", 13),
            ),
            Column(
                "Home",
                375,
                render_fn=lambda p, x, y, item: p.draw_text(x, y, "yes", 13, "accent") if item.ref.is_home() else None,
            ),
            Column(
                "",
                -60,
                render_fn=lambda p, x, y, item: self.draw_select_button(x, y, item.ref.id, "outpost"),
            ),
        ]

        self.draw_table(
            columns,
            self.outpost_list.values(),
            is_selected_fn=lambda item: self.is_selected(item.ref.id, "outpost"),
            selected_color_fill="#2a202f",
            selected_color_border="#462e60",
        )

    def draw_vehicle_list(self):
        columns = [
            Column(
                "Power",
                0,
                render_fn=lambda p, x, y, item: self.draw_battery(x, y, 60, 15, item.ref.battery.level()),
            ),
            Column(
                "Name",
                90,
                render_fn=lambda p, x, y, item: p.draw_text(x, y, item.ref.name, 13),
            ),
            # Column("Status", 275, render_fn=lambda p, x, y, item:
            #        self.draw_status_dot(x, y, self.get_vehicle_status_for_dot(item.ref.status()))),
            Column(
                "Type",
                350,
                render_fn=lambda p, x, y, item: p.draw_text(x, y, f"{item.ref.type_id}", 13),
            ),
            # Column("Task", 350, render_fn=lambda p, x, y, item:
            #        p.draw_text(x, y, "yes", 13, "accent") if not item.config.get("task") else None),
            Column(
                "",
                -60,
                render_fn=lambda p, x, y, item: self.draw_select_button(x, y, item.ref.id, "vehicle"),
            ),
        ]

        self.draw_table(
            columns,
            self.vehicle_list.values(),
            is_selected_fn=lambda item: self.is_selected(item.ref.id, "vehicle"),
        )

        # # TABLE HEADLINES
        # self.c.down()
        # # y += 40
        # # self.c.column(12)
        # self.panel.draw_text(self.c.x, self.c.y, "Battery", 13, "accent")
        # # self.c.pop()

        # self.c.column(90)
        # self.panel.draw_text(self.c.x, self.c.y, "Name", 13, "accent")
        # self.c.pop()

        # self.c.column(225)
        # self.panel.draw_text(self.c.x, self.c.y, "Status", 13, "accent")
        # self.c.pop()

        # self.c.column(280)
        # self.panel.draw_text(self.c.x, self.c.y, "Type", 13, "accent")
        # self.c.pop()

        # self.c.column(350)
        # self.panel.draw_text(self.c.x, self.c.y, "Task", 13, "accent")
        # self.c.pop()
        # # self.c.column(50)
        # # self.panel.draw_text(self.c.x, self.c.y, "Select", 13, "accent")
        # # self.c.pop()

        # # y += 35
        # self.c.next_row()
        # # self.c.column(10)
        # for id, item in self.vehicle_list.items():
        #     if self.is_selected(id, "vehicle"):
        #         self.panel.fill_rect(7, self.c.y - 14, self.panel.width() - 14, 27, "#192119")
        #         self.panel.draw_rect(7, self.c.y - 14, self.panel.width() - 14, 27, "#1a3917")
        #     # if index > 0:
        #     #     y += 35

        #     self.c.column(12)
        #     # Battery
        #     bat = item.ref.battery.level()
        #     self.panel.progress_bar(self.c.x, self.c.y - 8, 60, 15, bat, self.get_battery_color(bat))
        #     self.panel.draw_text(self.c.x + 15, self.c.y, f"{bat * 100}%", 13, "black")
        #     self.c.pop()

        #     # Name
        #     self.c.column(90)
        #     self.panel.draw_text(self.c.x, self.c.y, item.ref.name, 13)
        #     self.c.pop()

        #     # Status
        #     self.c.column(225)
        #     self.panel.status_dot(self.c.x + 25, self.c.y, 5, self.get_vehicle_status_for_dot(item.ref.status()))
        #     self.c.pop()

        #     # Type
        #     self.c.column(280)
        #     self.panel.draw_text(self.c.x, self.c.y, item.ref.type_id, 13)
        #     self.c.pop()

        #     # Task
        #     self.c.column(350)
        #     task: dict = item.config.get("task")
        #     if task:
        #         task: VehicleTask = VehicleTask(task)
        #         self.panel.draw_text(self.c.x, self.c.y, task.action, 13)
        #     else:
        #         self.panel.draw_text(self.c.x, self.c.y, "idle", 13)
        #     self.c.pop()

        #     # Select
        #     self.c.column(self.panel.width() - 80)
        #     if not self.is_selected(item.ref.id, "vehicle"):
        #         if self.panel.button(f"select.{item.ref.name}", self.c.x, self.c.y - 12, 50, 20, "select"):
        #             self.config.set("selected", { "type": "vehicle", "id": id })
        #     self.c.pop()
        #     self.c.next_row()

    def get_vehicle_status_for_dot(self, status: str) -> str:
        if status in self.VEHICLE_STATUS:
            return self.VEHICLE_STATUS[status]
        else:
            return self.VEHICLE_STATUS["default"]

    def is_selected(self, id: str, type: str) -> bool:
        selected: dict = self.config.get("selection")
        if not selected:
            return False

        return type in selected and selected[type] == id
