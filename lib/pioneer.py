from vehicle import VehicleController


class PioneerController(VehicleController):
    def __init__(self, ref: Pioneer):
        super().__init__(ref)
        self.ref: Pioneer
