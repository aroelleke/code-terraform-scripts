vault = self.contract.vault

directions = ["north", "east", "south", "west"]
opposites = {"north": "south", "east": "west", "south": "north", "west": "east"}

def transmit(key):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")
    transmitter.transmit(self.contract.id, key)

def get_pos_key(pos=None):
    if pos is None:
        pos = vault.position
    # Sichere Attribut- vs Dict-Abfrage
    row = pos.row if hasattr(pos, "row") else pos["row"]
    col = pos.col if hasattr(pos, "col") else pos["col"]
    return f"{col}-{row}"

def solve():
    path = []
    # Speichert pro Zelle: {richtung: status}
    visited = {}

    while True:
        curr_key = get_pos_key()
        if curr_key not in visited:
            visited[curr_key] = {}

        # Noch ungetestete Richtungen von der aktuellen Zelle aus
        untested_dirs = [d for d in directions if d not in visited[curr_key]]

        # Wenn wir schon Schritte gegangen sind, nicht direkt zurücklaufen
        if len(path) > 0:
            back_dir = opposites[path[-1]]
            move_candidates = [d for d in untested_dirs if d != back_dir]
        else:
            move_candidates = untested_dirs

        if len(move_candidates) > 0:
            # Vorwärts: Probiere die nächste ungetestete Richtung
            chosen_dir = move_candidates[0]
            result = vault.move(chosen_dir)
            visited[curr_key][chosen_dir] = result.status

            if result.status == "exit":
                escape_res = vault.escape()
                return escape_res.key
            elif result.status == "path":
                path.append(chosen_dir)
            # Bei "wall" bleibt die Position unverändert, nächste Iteration testet die nächste Richtung
        else:
            # Sackgasse: Backtracking
            if not path:
                raise Exception("Labyrinth unlösbar oder kein Ausgang erreichbar.")
            
            back_dir = opposites[path.pop()]
            res = vault.move(back_dir)
            if res.status == "exit":
                escape_res = vault.escape()
                return escape_res.key

def main():
    key = solve()
    print(f"Key: {key}")
    transmit(key)

main()