class BaseController:
    def __init__(self, ref):
        self.ref = ref

    def run(self):
        while True:
            self.iteration()

    def iteration(self):
        raise NotImplementedError("Please Implement this method")
