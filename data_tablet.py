tablet = self.contract.tablet

def transmit(message):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")

    transmitter.transmit(self.contract.id, message)
    
def main():
    message = ""
    
    for row in range(tablet.rows):
        for col in range(tablet.cols):
            result = tablet.probe(row, col)
            if result.distance == 0:
                message += result.char
    
    transmit(message)

main()