from base_controller import BaseController


class HeatGeneratorController(BaseController):
    def __init__(self, ref: TempHeater):
        super().__init__(ref)
        self.ref: TempHeater

        self.efficiency_table = {"clear": 5, "dust_storm": 3, "heat_bleed": 9, "dust_veil": 2}

    def iteration(self):
        if self.ref.efficiency() != 100:
            self.ref.set_power(self.efficiency_table[self.ref.thermal_state()])
