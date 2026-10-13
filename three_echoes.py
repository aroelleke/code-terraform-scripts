def transmit(subject) -> bool:
    transmitter = get_component("transmitter")
    transmitter.connect("earth")
    result = transmitter.transmit(self.contract.id, subject)

    return True if result == "correct" else False
    

def main():
    broadcast = self.contract.broadcast
    print(broadcast.freq_a)
    print(broadcast.freq_b)
    print(broadcast.freq_c)

    a = [c for c in broadcast.freq_a]
    b = [c for c in broadcast.freq_b]
    c = [c for c in broadcast.freq_c]

    total_length = len(a) + len(b) + len(c)

    code = ""
    for i in range(1, total_length + 1):
        match i % 3:
            case 1:
                code = code + a.pop(0)
            case 2:
                code = code + b.pop(0)
            case 0:
                code = code + c.pop(0)

    code = code.lower()
    
    print(code)
    transmit(code)

main()
