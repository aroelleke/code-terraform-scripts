def transmit(code):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")
    result = transmitter.transmit(self.contract.id, code)

    return True if result == "correct" else False
    

def char_down(char: string, count: int):
    if char.isspace():
        return char
        
    char_ord = ord(char)
    new_ord = char_ord - count

    # below "A", return to "Z"
    if new_ord <= 64:
        rest = 64 - new_ord
        new_ord = 90 - rest
    return chr(new_ord)
    

def main():
    device = self.contract.device
    print("Code: ", device.slabs)
    
    for i in range(1, 26):
        code = [char_down(c, i) for c in device.slabs]
        code = "".join(code)
        
        if transmit(code):
            break
        

main()
