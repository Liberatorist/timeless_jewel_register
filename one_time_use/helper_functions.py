
import json


with open("static/tree.json", "r") as file:
    tree = json.loads(file.read())

def in_radius(node_id1, node_id2, radius):
    return (tree[node_id1]["x"]  - tree[node_id2]["x"]) ** 2 +\
            (tree[node_id1]["y"]  - tree[node_id2]["y"]) ** 2 <= radius**2
