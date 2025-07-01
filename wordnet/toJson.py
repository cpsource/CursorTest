import json

# The tree as a multiline string:
tree_text = """Sense 1
dog, domestic dog, Canis familiaris
       => canine, canid
           => carnivore
               => placental, placental mammal, eutherian, eutherian mammal
                   => mammal, mammalian
                       => vertebrate, craniate
                           => chordate
                               => animal, animate being, beast, brute, creature, fauna
                                   => organism, being
                                       => living thing, animate thing
                                           => whole, unit
                                               => object, physical object
                                                   => physical entity
                                                       => entity
       => domestic animal, domesticated animal
           => animal, animate being, beast, brute, creature, fauna
               => organism, being
                   => living thing, animate thing
                       => whole, unit
                           => object, physical object
                               => physical entity
                                   => entity
"""

def parse_tree(text):
    lines = text.strip().splitlines()
    stack = []
    root = None

    for line in lines:
        # skip "Sense 1"
        if line.startswith("Sense"):
            continue

        # Count leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        # Each indent level = 4 spaces
        level = leading_spaces // 4

        # Remove indentation and symbols
        content = line.strip()
        if content.startswith("=>"):
            content = content[2:].strip()

        # Create node
        node = {
            "name": content,
            "children": []
        }

        if level == 0:
            root = node
            stack = [node]
        else:
            # Find parent at previous level
            while len(stack) > level:
                stack.pop()
            parent = stack[-1]
            parent["children"].append(node)
            stack.append(node)

    return root

if __name__ == "__main__":
    tree_json = parse_tree(tree_text)
    print(json.dumps(tree_json, indent=2))


