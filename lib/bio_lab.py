from base_controller import BaseController
from dataclasses import dataclass
from machine_store import MachineStore


@dataclass
class BioLabConfig:
    auto_buy_ingredients: bool = True


class BioLabController(BaseController):
    def __init__(self, ref: BioLab, input: str = "inventory", output: str = "inventory"):
        super().__init__(ref)
        self.ref: BioLab

        self.store: MachineStore[BioLabConfig] = MachineStore(f"bio_lab.{ref.id}", BioLabConfig)

        self.bio_collector: BioCollector | None = self.get_bio_collector()
        self.inventory: Inventory = get_component("inventory")
        self.shop: Shop = get_component("shop")

        # Connect I/O to inventory
        self.ref.input.connect(input)
        self.ref.output.connect(output)

    def get_bio_collector(self) -> BioCollector | None:
        bio_collector: list[BuildingRef] = ref.outpost.buildings("bio_collector")
        if bio_collector:
            b: BuildingRef = bio_collector[0]
            return get_component(b.id)

    def handle_specimen(self):
        # Check if specimen is loaded, try to load otherwise
        if not self.ref.specimen:
            result = self.ref.take_from(self.bio_collector)

            if result.status != "ok":
                if result.status != "source_empty":
                    print(f'[INFO] Status: "{result.status}" - "{result.message}"')
                return False

        if self.ref.specimen.stage == "collected":
            self.ref.analyze()

        return True

    # TODO: Refactor
    def iteration(self):
        if not self.handle_specimen():
            return

        recipe = self.ref.specimen.recipe

        # Get reagents from inventory or buy them
        for reagent_id, count in recipe.items():
            self.clean_input()

            available = self.get_available_in_inventory(reagent_id)

            if available < count:
                # Buy missing
                if self.store.config.auto_buy_ingredients:
                    missing = count - available
                    self.shop.buy(reagent_id, missing)

            # Prevent input from overflowing
            capacity = self.ref.input.capacity()
            loaded = 0
            while loaded < count:
                input = capacity if count > capacity else count - loaded

                self.ref.input.take(reagent_id, input)
                self.ref.load(reagent_id, input)

                loaded += input

        # Recipe is loaded
        result = self.ref.extract()
        if result.status == "ok":
            print("INFO: Extraction successful!")
        else:
            print(f'INFO: Extraction failed! "status": "{result.status}", "message": "{result.message}"')

        # Empty output
        for stack in self.ref.output.stacks():
            print(f"Found in output: {stack.id} -> {stack.count}")
            self.ref.output.send(stack.id, stack.count, stack.properties)

    # TODO: outsource into an inventory class
    def get_available_in_inventory(self, item_id: str) -> int:
        inventory = self.inventory

        return sum([slot.count for slot in inventory.get_slots() if slot.id == item_id])

    def clean_input(self):
        input = self.ref.input

        if input.count() > 0:
            # TODO: should´t be hardcoded
            EJECT_TO = "inventory"
            print(f'[INFO]: Input is filled, ejecting to "{EJECT_TO}"')

            for stack in input.stacks():
                input.eject(EJECT_TO, stack.id, stack.count, stack.properties)
                print(f'[INFO]: Ejected {stack.count}x "{stack.id}"')
