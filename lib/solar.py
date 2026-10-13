from base_controller import BaseController


class SolarGeneratorController(BaseController):
    def __init__(self, ref: SolarGenerator):
        super().__init__(ref)
        self.ref: SolarGenerator

        self.clock: Clock = get_component("clock")

    def iteration(self):
        self.ref.set_tilt(90 - self.clock.get_elevation())
