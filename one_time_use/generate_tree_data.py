

import json
import math
from typing import Tuple

from urllib import request


def getOrbitAngle(t, e):
    i = .017453293
    if e == 40:
        if t == 0:
            return getOrbitAngle(0, 12)
        if t == 1:
            return getOrbitAngle(0, 12) + 10 * i
        if t == 2:
            return getOrbitAngle(0, 12) + 20 * i
        if t == 3:
            return getOrbitAngle(1, 12)
        if t == 4:
            return getOrbitAngle(1, 12) + 10 * i
        if t == 5:
            return getOrbitAngle(1, 12) + 15 * i
        if t == 6:
            return getOrbitAngle(1, 12) + 20 * i
        if t == 7:
            return getOrbitAngle(2, 12)
        if t == 8:
            return getOrbitAngle(2, 12) + 10 * i
        if t == 9:
            return getOrbitAngle(2, 12) + 20 * i
        if t == 10:
            return getOrbitAngle(3, 12)
        if t == 11:
            return getOrbitAngle(3, 12) + 10 * i
        if t == 12:
            return getOrbitAngle(3, 12) + 20 * i
        if t == 13:
            return getOrbitAngle(4, 12)
        if t == 14:
            return getOrbitAngle(4, 12) + 10 * i
        if t == 15:
            return getOrbitAngle(4, 12) + 15 * i
        if t == 16:
            return getOrbitAngle(4, 12) + 20 * i
        if t == 17:
            return getOrbitAngle(5, 12)
        if t == 18:
            return getOrbitAngle(5, 12) + 10 * i
        if t == 19:
            return getOrbitAngle(5, 12) + 20 * i
        if t == 20:
            return getOrbitAngle(6, 12)
        if t == 21:
            return getOrbitAngle(6, 12) + 10 * i
        if t == 22:
            return getOrbitAngle(6, 12) + 20 * i
        if t == 23:
            return getOrbitAngle(7, 12)
        if t == 24:
            return getOrbitAngle(7, 12) + 10 * i
        if t == 25:
            return getOrbitAngle(7, 12) + 15 * i
        if t == 26:
            return getOrbitAngle(7, 12) + 20 * i
        if t == 27:
            return getOrbitAngle(8, 12)
        if t == 28:
            return getOrbitAngle(8, 12) + 10 * i
        if t == 29:
            return getOrbitAngle(8, 12) + 20 * i
        if t == 30:
            return getOrbitAngle(9, 12)
        if t == 31:
            return getOrbitAngle(9, 12) + 10 * i
        if t == 32:
            return getOrbitAngle(9, 12) + 20 * i
        if t == 33:
            return getOrbitAngle(10, 12)
        if t == 34:
            return getOrbitAngle(10, 12) + 10 * i
        if t == 35:
            return getOrbitAngle(10, 12) + 15 * i
        if t == 36:
            return getOrbitAngle(10, 12) + 20 * i
        if t == 37:
            return getOrbitAngle(11, 12)
        if t == 38:
            return getOrbitAngle(11, 12) + 10 * i
        if t == 39:
            return getOrbitAngle(11, 12) + 20 * i
    elif e==16:
        if t == 0:
            return 0
        if t == 1:
            return 30 * i
        if t == 2:
            return 45 * i
        if t == 3:
            return 60 * i
        if t == 4:
            return 90 * i
        if t == 5:
            return 120 * i
        if t == 6:
            return 135 * i
        if t == 7:
            return 150 * i
        if t == 8:
            return 3.14159274
        if t == 9:
            return 210 * i
        if t == 10:
            return 225 * i
        if t == 11:
            return 240 * i
        if t == 12:
            return 4.71238911
        if t == 13:
            return 300 * i
        if t == 14:
            return 315 * i
        if t == 15:
            return 330 * i
    return 2 * math.pi * t / e

def passive_node_coordinates(node: dict, tree: dict) -> Tuple[float, float]:
    orbit_radius = tree['constants']['orbitRadii'][node['orbit']]
    n_skills = tree['constants']['skillsPerOrbit'][node['orbit']]
    group = tree['groups'][str(node['group'])]
    angle = getOrbitAngle(node['orbitIndex'], n_skills) - math.pi / 2
    x = group['x'] + orbit_radius * math.cos(angle)
    y = group['y'] + orbit_radius * math.sin(angle)
    return x, y, group['x'], group['y'], angle, orbit_radius


def get_node_type(node: dict) -> str:
    if node.get("isMastery") is not None:
        return "mastery"
    if node.get("isKeystone") is not None:
        return "keystone"
    if node.get("isJewelSocket") is not None:
        return "jewel_socket"
    if node.get("isAscendancyStart") is not None:
        return "ascendancy_start"
    if node.get("isBlighted") is not None:
        return "blight"
    if node.get("classStartIndex") is not None:
        return "class_start"
    if node.get("isNotable") is not None:
        return "notable"
    return "small"

def set_drawable(node: dict) -> str:
    if node.get("isProxy") is not None:
        return False
    if node["name"] in ["Small Jewel Socket", "Medium Jewel Socket"]:
        return False
    if node.get("isMastery") is not None:
        return False
    if node.get("isKeystone") is not None:
        return True
    if node.get("isJewelSocket") is not None:
        return True
    if node.get("isAscendancyStart") is not None:
        return True
    if node.get("isBlighted") is not None:
        return True
    if node.get("classStartIndex") is not None:
        return False
    if node.get("isNotable") is not None:
        return True
    return True


def remove_portals(tree_data):
    for node_id, node in tree_data["nodes"].items():
        if node.get("grantedPassivePoints") == 2 or node.get("classStartIndex") is not None:
            node["cantBeConnectedTo"] = True
    return tree_data

def get_tree():
    with open("data/tree_data.json", "r") as file:
        tree_data = json.loads(file.read())
    tree = {}
    tree_data = remove_portals(tree_data)
    for node_id, node in tree_data["nodes"].items():
        if node_id == "root" or "group" not in node or not set_drawable(node):
            continue

        if "orbit" in node:
            x, y, cx, cy, angle, orbit_radius = passive_node_coordinates(
                node, tree_data)
        
        tree[node_id] = {"x": round(x, 2), "y": round(y, 2), "cx": round(cx, 2), "cy": round(cy, 2), "angle": round(angle, 4), 
                        "orbit_radius": orbit_radius, "group": node["group"], "in": node["in"],
                        "orbit": node["orbit"], "skill": node["skill"], "type": get_node_type(node)}
        if node.get("cantBeConnectedTo"):
            tree[node_id]["cantBeConnectedTo"] = True
    return tree

if __name__ == "__main__":
    with open("static/tree.json", "w") as file:
        file.write(json.dumps(get_tree(), separators=(',', ':')))

