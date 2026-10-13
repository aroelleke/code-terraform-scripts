lock = self.contract.lock

def transmit(code):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")
    
    transmitter.transmit(self.contract.id, code)

def main():
    code = [0, 0, 0, 0, 0, 0]
    
    for t in range(lock.tumblers):
        for r in range(lock.range):
            code[t] = r
            result = lock.intercept(code)
            
            if result[t]:
                break
    
    transmit(code)

main()