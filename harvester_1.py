scanner = get_component("scanner_1")
inventory = get_component("inventory")

harvested_sectors = set()

def main():
    current_target = None

    while True:
        start_position = self.get_position()
        
        # set next target
        if not current_target:
            current_target = get_next_target(start_position)

            # no target left
            if not current_target:
                break

        # move to current target
        move_to_target(current_target, start_position)
        
        # collect resources and store in inventory
        pickup = self.collect()
        if pickup.status == "holding":
            self.store()
            harvested_sectors.add(current_target)
            current_target = None

def sector_to_coords(sector):
    return ord(sector[0]) - 65, int(sector[1:])

def coords_to_sector(row, col):
    return f"{chr(row + 65)}{col}"

def manhattan_dist(c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])

def get_next_target(start_position):
    scanned = scanner.get_scanned()

    targets = dict()
    
    for sector, scan in scanned.items():
        if not scan.status == "ok" or sector in harvested_sectors:
            continue
    
        distance = manhattan_dist(sector_to_coords(start_position), sector_to_coords(sector))

        #  prevent divide by zero if harvester is already positioned at sector
        if not distance == 0:
            value_per_distance = scan.value / distance
        else:
            value_per_distance = 999999
            
        targets[sector] = value_per_distance

    # no targets left
    if not targets:
        return None
        
    # return target with highest value per distance
    return max(targets, key=targets.get)

def move_to_target(target, start_position):
    position = start_position
    target_row, target_column = sector_to_coords(target)
    
    while not position == target:
         # manage heat and wait if heat exceeds 80% of max
        if self.get_heat() >= self.get_max_heat() * 0.8:
            while self.get_heat() >= self.get_max_heat() * 0.1:
                pass
        
        current_row, current_column = sector_to_coords(position)

        next_row = current_row
        next_column = current_column

        if current_row != target_row:
            next_row += 1 if current_row < target_row else -1
        elif current_column != target_column:
            next_column += 1 if current_column < target_column else -1
        
        self.move(coords_to_sector(next_row, next_column))
        position = self.get_position()

main()