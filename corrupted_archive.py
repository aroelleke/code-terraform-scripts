archive = self.contract.archive

def transmit(pairs):
    transmitter = get_component("transmitter")
    transmitter.connect("earth")

    transmitter.transmit(self.contract.id, pairs)

def main():
    pairs_temp = dict()
    
    for col in range(archive.cols):
        for row in range(archive.rows):
            word = archive.flip(row, col)

            if not pairs_temp.has(word):
                pairs_temp[word] = []                
            
            pairs_temp[word].append([row, col])

    
    pairs = []
    for word, items in pairs_temp.items():
        pairs.append([items[0][0], items[0][1], items[1][0], items[1][1]])
    
    transmit(pairs)

main()
