from base_controller import BaseController
from dataclasses import dataclass
from machine_store import MachineStore


@dataclass
class BioExchangeConfig:
    auto_select_order: bool = True


class BioExchangeController(BaseController):
    def __init__(self, ref: BioExchange, input: str = "inventory", output: str = "inventory"):
        super().__init__(ref)
        self.ref: BioExchange

        self.store: MachineStore[BioExchangeConfig] = MachineStore(f"bio_exchange.{ref.id}", BioExchangeConfig)

        self.planet: Nocturna = get_component("nocturna")
        self.outpost: Outpost = get_component(ref.outpost.id)
        self.inventory: Inventory = get_component("inventory")

        # Connect I/O to inventory
        self.ref.input.connect(input)
        self.ref.output.connect(output)

    def iteration(self):
        # No order is currently valid
        if not self.check_active_order():
            return
        self.clean_input()
        self.handle_order()

    def check_active_order(self) -> bool:
        if self.ref.active_order():
            return True

        order_id = self.get_next_order()
        if not order_id:
            return False

        self.ref.set_order(order_id)
        return True

    def handle_order(self):
        required = self.get_required()

        # Get required items and deliver them
        for item_id, count in required.items():
            available = self.get_available_in_inventory(item_id)

            if available == 0:
                # TODO: setup automated requests through signal busses
                continue

            self.ref.input.take(item_id, min(count, available))
            self.ref.deliver()

    def get_required(self):
        requires = self.ref.active_order().requires
        delivered = self.ref.active_order().delivered

        left = dict()

        for item_id, count in requires.items():
            left[item_id] = count - delivered.get(item_id, 0)

        return left

    # TODO: outsource into an inventory class
    def get_available_in_inventory(self, item_id: str) -> int:
        return sum([slot.count for slot in self.inventory.get_slots() if slot.id == item_id])

    def get_next_order(self):
        order_id = self.get_order_from_comms()

        if not order_id:
            if self.store.config.auto_select_order:
                order_id = self.auto_select_order()

        return order_id

    def get_order_from_comms(self) -> str:
        task = self.comms.next()
        if task:
            return task.value["order_id"]

    def auto_select_order(self) -> str:
        order_ids = self.get_valid_orders()
        return order_ids[0] if len(order_ids) else None

    def get_valid_orders(self):
        current_biome = self.get_current_biome()
        return [order.id for order in self.ref.orders() if order.status == "available" and order.biome == current_biome]

    # TODO: outsource into outpost class
    def get_current_biome(self):
        coords = self.outpost.coords()
        return self.planet.biome_at(coords[0], coords[1])

    def clean_input(self, target_inventory: str = "inventory"):
        if self.ref.input.count() > 0:
            for stack in self.ref.input.stacks():
                self.ref.input.eject(target_inventory, stack.id, stack.count, stack.properties)
