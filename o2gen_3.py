atmosphere = get_component("atmosphere")

def main():
    while True:
        co2 = atmosphere.get_co2()
        self.set_intake(co2 / 10)
        
        waste = self.waste()
        if waste >= 60:
            self.dump_waste()

main()
