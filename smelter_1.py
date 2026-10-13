inventory = get_component("inventory")

# Connect I/O to inventory
self.input.connect("inventory")
self.output.connect("inventory")

# Get available recipes for which materials are in connected inventory
def get_craftable_recipes():
    craftable_recipes = []
    
    for recipe in self.list_recipes():
        for item in recipe.inputs:
            if inventory.get_count(item) >= recipe.inputs[item]:
                craftable_recipes.append(recipe)

    return craftable_recipes

def craft_recipe(recipe):
    self.set_recipe(recipe)
    self.input.capacity()

    for input in recipe.inputs:
        self.input.take(input, recipe.inputs[input])


def main():
    current_recipe = None
    
    while True:
        if self.is_running():
            continue

        if self.output.count() > 0:
            self.get_recipe()
            self.output.send()

        craftable_recipes = get_craftable_recipes()
        if craftable_recipes.length == 0:
            continue

        current_recipe = craftable_recipes[0]
        craft_recipe(current_recipe)

main()