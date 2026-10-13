def transmit(message: string):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")
    transmitter.transmit(self.contract.id, message)


def list_to_string(list: List[number]) -> string:
    return "".join([chr(i + 64) for i in list])


def main():
    program = self.contract.program
    print("Program: ", program)
    
    memory = program[:]
    ip = 0
    output = list()

    while True:
        instruction = memory[ip]
        # make sure instruction contains 4 digits
        instruction_str = str(instruction).zfill(4)
        
        param_1_modi = instruction_str[1]
        param_2_modi = instruction_str[0]
        opcode = instruction_str[-2:]
        
        match opcode:
            case "01":
                param_1 = memory[ip + 1] if param_1_modi == "1" else memory[memory[ip + 1]]
                param_2 = memory[ip + 2] if param_2_modi == "1" else memory[memory[ip + 2]]
                destination = memory[ip + 3]

                memory[destination] = param_1 + param_2

                ip += 4
            case "02":
                param_1 = memory[ip + 1] if param_1_modi == "1" else memory[memory[ip + 1]]
                param_2 = memory[ip + 2] if param_2_modi == "1" else memory[memory[ip + 2]]
                destination = memory[ip + 3]

                memory[destination] = param_1 * param_2

                ip += 4
            case "04":
                param_1 = memory[ip + 1] if param_1_modi == "1" else memory[memory[ip + 1]]
                output.append(param_1)

                ip += 2
            case "05":
                condition = memory[ip + 1] if param_1_modi == "1" else memory[memory[ip + 1]]
                jump_target = memory[ip + 2] if param_2_modi == "1" else memory[memory[ip + 2]]

                if condition != 0:
                    ip = jump_target
                else:
                    ip += 3
            case "99":
                 break

    message = list_to_string(output)
    print("Message: ", message)
    transmit(message)

main()
