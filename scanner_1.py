rows = 8
columns = 24

def main():
    while True:
        for column in range(columns):
            for row in range(rows):
                sector = coords_to_sector(row, column + 1)
                self.scan(sector)

        sleep(60)

def sector_to_coords(sector):
    return ord(sector[0]) - 65, int(sector[1:])

def coords_to_sector(row, col):
    return f"{chr(row + 65)}{col}"

main()