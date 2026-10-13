from vehicle import VehicleController


class RoverController(VehicleController):
    def __init__(self, ref: Rover):
        super().__init__(ref)
        self.ref: Rover
