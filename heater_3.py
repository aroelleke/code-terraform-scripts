def main():
    efficiency_table = {
        "clear": 5, 
        "dust_storm": 3,
        "heat_bleed": 9,
        "dust_veil": 2
    }
    
    while True:
        # do nothing as long as efficiency is at 100%
        if self.efficiency() == 100:
            continue
        
        thermal_state = self.thermal_state()
        if efficiency_table[thermal_state]:
            power = efficiency_table[thermal_state]
            self.set_power(power)
            continue

main()