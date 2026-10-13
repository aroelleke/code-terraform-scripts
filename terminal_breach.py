terminal = self.contract.terminal

def transmit(code):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")
    
    transmitter.transmit(self.contract.id, code)

# Prepares the code with required length and a 1 at every position
def prepare_code():
    code = range(terminal.length)
    for position in code:
        code[position] = 1
    return code

# Recursivly call itself until correct code is found
def recursively_solve_passcode(code, position, correct):
    # Check every possible digit
    for digit in range(1, 6):
        # Guess with current code
        code[position] = digit
        result = terminal.guess(code)

        # Nothing changed
        if result.correct == correct:
            continue

        # Previous digit was right, reset it
        if result.correct < correct:
            code[position] = digit - 1
        # Correct digit found, update correct state
        elif result.correct > correct:
            correct = result.correct

        # Check last position has been reached and if so, return correct code
        if position + 1 == terminal.length:
            return code
        else:
            # Move on to solve next position
            return recursively_solve_passcode(code, position + 1, correct)

def main():
    code = prepare_code()

    # Get initial correct count
    result = terminal.guess(code)
    
    code = recursively_solve_passcode(code, 0, result.correct)
    
    transmit(code)

main()