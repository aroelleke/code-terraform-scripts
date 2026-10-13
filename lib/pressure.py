from base_controller import BaseController


class PressureGeneratorController(BaseController):
    def __init__(self, ref: PressureGenerator):
        super().__init__(ref)
        self.ref: PressureGenerator

    def iteration(self):
        if self.ref.gauge() > self.ref.next_window_low() and self.ref.gauge() < self.ref.next_window_high():
            self.ref.sync()
