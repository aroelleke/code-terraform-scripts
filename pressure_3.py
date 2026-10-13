def main():
    while True:
        if self.gauge() > self.next_window_low() and self.gauge() < self.next_window_high():
            self.sync()

main()