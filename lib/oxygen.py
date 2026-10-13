from base_controller import BaseController


class OxygenGeneratorController(BaseController):
    def __init__(self, ref: OxygenGenerator):
        super().__init__(ref)
        self.ref: OxygenGenerator

        self.atmosphere: Atmosphere = get_component("atmosphere")

    def iteration(self):
        self.ref.set_intake(self.atmosphere.get_co2() / 10)

        if self.ref.waste() >= 60:
            self.ref.dump_waste()
