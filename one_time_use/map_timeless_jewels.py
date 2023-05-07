from enum import Enum
import io
import os, stat
import json
import math
from time import time
import zipfile
from steiner_interface import SteinerSolver




def get_passives_needed(jewel_id, anchor_points, aura_effect_nodes):
    terminals = [jewel_id] + list(anchor_points) + list(aura_effect_nodes)
    solver = SteinerSolver()
    steiner_nodes = solver.get_steiner_tree_for_terminals(terminals)
    return steiner_nodes


with open("data/jewel_slots.json", "r") as file:
    jewel_slots = json.loads(file.read())
with open("data/in_radius_of_jewel.json", "r") as file:
    in_jewel_radius = json.loads(file.read())
with open("data/in_radius_of_keystone.json", "r") as file:
    passives_for_keystone = {int(k): set(v) for k, v in json.loads(file.read()).items()}
with open("data/aura_nodes_by_seed.json", "r") as file:
    aura_nodes_by_seed = json.loads(file.read())



class TimelessJewelType(Enum):
	GLORIOUS_VANITY = 'Glorious Vanity'
	LETHAL_PRIDE = 'Lethal Pride'
	BRUTAL_RESTRAINT = 'Brutal Restraint'
	MILITANT_FAITH = 'Militant Faith'
	ELEGANT_HUBRIS = 'Elegant Hubris'


seed_ranges = {
    TimelessJewelType.GLORIOUS_VANITY: range(100, 8001),
    TimelessJewelType.LETHAL_PRIDE: range(10000, 18001),
    TimelessJewelType.BRUTAL_RESTRAINT: range(500, 8001),
    TimelessJewelType.MILITANT_FAITH: range(2000, 10001),
    TimelessJewelType.ELEGANT_HUBRIS: range(2000, 160001, 20),
}

min_effect = {
    TimelessJewelType.GLORIOUS_VANITY: 24,
    TimelessJewelType.LETHAL_PRIDE: 24,
    TimelessJewelType.BRUTAL_RESTRAINT: 16,
    TimelessJewelType.MILITANT_FAITH: 16,
    TimelessJewelType.ELEGANT_HUBRIS: 24,
}

def get_effect(jewel_type, aura_nodes):


    if jewel_type == TimelessJewelType.BRUTAL_RESTRAINT:
        return len(aura_nodes) * 8
    if jewel_type == TimelessJewelType.ELEGANT_HUBRIS:
        return len(aura_nodes) * 12
    # todo: glorious vanity
    return None


# def save_elegant_hubris_to_db(seed, passives, alt_passives):
#     con = sqlite3.connect('timeless.db')
#     sql = "INSERT INTO ACTIONS (JEWEL_TYPE, SEED, NODE_ID, ALT_PASSIVE_ID) VALUES(?, ?, ?, ?)"

#     data = [(0, seed, p, ap[1]) for p, ap in zip(passives, alt_passives)]

#     con.cursor().executemany(sql, data)
#     con.commit()
#     con.close()

def get_timeless_node_mapping():
    data={}
    for jewel_type in [TimelessJewelType.BRUTAL_RESTRAINT, TimelessJewelType.ELEGANT_HUBRIS, TimelessJewelType.GLORIOUS_VANITY]:
        data[jewel_type.value] = {}
        with open(f'data/TimelessJewels/{jewel_type.value.lower().replace(" ", "_")}_passives.txt', 'r', encoding='utf8') as file:
            passives = [int(line) for line in file.read().split('\n') if line != '']

        with open("steiner_solver/node_mapping.json", "r") as file:
            normalize = {int(k): v for k, v in json.loads(file.read()).items()}

        with zipfile.ZipFile(f'data/TimelessJewels/{jewel_type.value.lower().replace(" ", "_")}.zip') as archive:
            for seed in seed_ranges[jewel_type]:

                with archive.open(f'{seed}.csv', 'r') as infile:
                    alt_passives = [
                        line.split(',') for line in io.TextIOWrapper(infile, 'utf-8').read().split('\n')
                    ]
                    nodes = []
                    values = []
                    for p, ap in zip(passives, alt_passives):
                        if p not in normalize: # weird nodes. todo: fix timeless jewel generator maybe
                            # print(p)
                            continue
                        for apk, apv in zip(ap[1::2], ap[2::2]):
                            if apk=="3835":
                                nodes.append(p)
                                values.append(int(apv))
                    data[jewel_type.value][seed] = [nodes, values]

    with open("data/aura_nodes_by_seed.json", "w") as file:
        file.write(json.dumps(data, separators=(',', ':')))



notable_hashes_for_jewels = [
	'26725', '36634', '33989', '41263', '60735', '61834', '31683', '28475', '6230', '48768', '34483', '7960',
	'46882', '55190', '61419', '2491', '54127', '32763', '26196', '33631', '21984', '29712', '48679', '9408',
	'12613', '16218', '2311', '22994', '40400', '46393', '61305', '12161', '3109', '49080', '17219', '44169',
	'24970', '36931', '14993', '10532', '23756', '46519', '23984', '51198', '61666', '6910', '49684', '33753',
	'18436', '11150', '22748', '64583', '61288', '13170', '9797', '41876', '59585',
]

def in_radius(node_id1, node_id2, radius):
    return (tree[node_id1]["x"]  - tree[node_id2]["x"]) ** 2 +\
            (tree[node_id1]["y"]  - tree[node_id2]["y"]) ** 2 <= radius**2

with open("static/tree.json", "r") as file:
    tree = json.loads(file.read())
def get_passives_in_radius_of_jewel_slots():
    data = {}
    for jewel_id in notable_hashes_for_jewels:
        if jewel_id not in tree:
            continue
        data[jewel_id] = []
        for node_id, node in tree.items():
            if node["type"] in ["notable", "small"] and in_radius(node_id, jewel_id, 1800):
                data[jewel_id].append(int(node_id))

    with open("data/in_radius_of_jewel.json", "w") as file:
        file.write(json.dumps(data, separators=(',', ':')))


def get_passives_in_radius_of_keystones():
    data = {}
    for keystone_id, keystone in tree.items():
        if keystone["type"] != "keystone":
            continue
        data[keystone_id] = []
        for node_id, node in tree.items():
            if node["type"] in ["notable", "small"] and in_radius(node_id, keystone_id, 960):
                data[keystone_id].append(int(node_id))

    with open("data/in_radius_of_keystone.json", "w") as file:
        file.write(json.dumps(data, separators=(',', ':')))


def get_cost(nodes, jewel_type, slot):
    if jewel_slots[jewel_type.value][slot].get("exact_cost"):
        return jewel_slots[jewel_type.value][slot].get("exact_cost")
    else:
        return len(nodes) - jewel_slots[jewel_type.value][slot]['normal_pathing_cost']

def find_solution_without_anoint(jewel_type, jewel_id, slot, aura_nodes, effect_values):
    steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=jewel_slots[jewel_type.value][slot]["anchors"], aura_effect_nodes=aura_nodes)
    return {
        "slot": slot,
        "steiner_tree": steiner_tree_nodes,
        "aura_nodes": list(aura_nodes),
        "cost": get_cost(steiner_tree_nodes, jewel_type, slot),
        "anoint": [],
        "ie": [],
    }

def find_solution_with_anoint(jewel_type, jewel_id, slot, aura_nodes, effect_values):
    node_to_anoint = 0
    points_with_anoint = math.inf
    steiner_nodes_with_anoint = []
    for node in aura_nodes:
        anoint_nodes = set(aura_nodes) - {node}
        steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=jewel_slots[jewel_type.value][slot]["anchors"], aura_effect_nodes=anoint_nodes)
        if len(steiner_tree_nodes) < points_with_anoint:
            node_to_anoint = node
            points_with_anoint = len(steiner_tree_nodes)
            steiner_nodes_with_anoint = steiner_tree_nodes

    steiner_tree_nodes = steiner_nodes_with_anoint + [node_to_anoint]
    return {
        "slot": slot,
        "steiner_tree": steiner_tree_nodes,
        "aura_nodes": list(aura_nodes),
        "cost": get_cost(steiner_tree_nodes, jewel_type, slot),
        "anoint": [node_to_anoint],
        "ie": [],
    }



def find_solution_with_ie(jewel_type, jewel_id, slot, aura_nodes, effect_values):
    for keystone_id, passives_around_keystone in passives_for_keystone.items():
        if len(set(aura_nodes) & passives_around_keystone) >= 2:
            remaining_nodes = set(aura_nodes) - passives_around_keystone
            steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=jewel_slots[jewel_type.value][slot]["anchors"], aura_effect_nodes=remaining_nodes)
            steiner_tree_nodes += list(set(aura_nodes) & passives_around_keystone)
            return {
                "slot": slot,
                "steiner_tree": steiner_tree_nodes,
                "aura_nodes": list(aura_nodes),
                "cost": get_cost(steiner_tree_nodes, jewel_type, slot),
                "anoint": [],
                "ie": [keystone_id],
            }
    return None


def iteratively_cull_nodes(nodes, effects, min_effect):
    yield nodes, effects
    for node, effect in zip(nodes, effects):
        culled_nodes = [n for n in nodes if n!=node]
        culled_effects = [e for e in effects if e!=effect]
        if sum(culled_effects) < min_effect:
            continue
        for n, e in iteratively_cull_nodes(culled_nodes, culled_effects, min_effect):
            yield n, e

def get_worthwhile_passive_combinations(nodes, effects, min_effect):
    already_seen = set()
    for n, e in iteratively_cull_nodes(nodes, effects, min_effect):
        if tuple(n) not in already_seen:
            already_seen.add(tuple(n))
            yield n, e        

def fetch_solutions():
    t = time()
    solutions = []
    for jewel_type in [TimelessJewelType.BRUTAL_RESTRAINT, TimelessJewelType.ELEGANT_HUBRIS, TimelessJewelType.GLORIOUS_VANITY]:
        for slot in jewel_slots[jewel_type.value]:
            jewel_id = jewel_slots[jewel_type.value][slot]["jewel_hash"]
            passives_in_radius = set(in_jewel_radius[str(jewel_id)])

            if jewel_type == TimelessJewelType.BRUTAL_RESTRAINT:
                passives_in_radius &= {37078, 10835, 3452, 45067, 21602, 65097, 33545, 19506, 44103, 35958, 11730, 27137}

            for seed in seed_ranges[jewel_type]:
                aura_nodes = []
                effect_values = []
                a = aura_nodes_by_seed[jewel_type.value][str(seed)]
                for aura_node, aura_effect in zip(a[0], a[1]):
                    if aura_node in passives_in_radius:
                        aura_nodes.append(aura_node)
                        effect_values.append(aura_effect)

                effect = sum(effect_values)


                if effect >= min_effect[jewel_type]:
                    print(jewel_type, slot, seed, effect)
                    for aura_nodes, effect_values in get_worthwhile_passive_combinations(aura_nodes, effect_values, min_effect[jewel_type]):
                        solution = find_solution_without_anoint(jewel_type, jewel_id, slot, aura_nodes, effect_values)
                        solutions.append({"seed": seed, "type": jewel_type.value, "effect": sum(effect_values), **solution})

                        if jewel_type == TimelessJewelType.BRUTAL_RESTRAINT:
                            continue

                        solution = find_solution_with_ie(jewel_type, jewel_id, slot, aura_nodes, effect_values)
                        if solution:
                            solutions.append({"seed": seed, "type": jewel_type.value, "effect": sum(effect_values), **solution})

                        if effect >= 36:
                            solution = find_solution_with_anoint(jewel_type, jewel_id, slot, aura_nodes, effect_values)
                            solutions.append({"seed": seed, "type": jewel_type.value, "effect": sum(effect_values), **solution})


    with open("data/steiner_solutions.json", "w") as file:
        file.write(json.dumps(solutions, separators=(',', ':')))
    print(time()-t)

def clean_up_data():
    with open("data/steiner_solutions.json", "r") as file:
        data = json.loads(file.read())
    data_dict = {}

    for solution in data:
        if solution["effect"] / solution["cost"] <= 2.5:
            continue
        key = (solution["type"],solution["seed"],solution["slot"])
        if key not in data_dict:
            data_dict[key] = []
        data_dict[key].append(solution)
    solutions = []
    for k, v in data_dict.items():
        cutoffs = [(s["effect"], s["effect"]/s["cost"]) for s in v if not (s["ie"] or s["anoint"])]
        cutoffs_ie = [(s["effect"], s["effect"]/s["cost"]) for s in v if s["ie"]]
        cutoffs_anoints = [(s["effect"], s["effect"]/s["cost"]) for s in v if s["anoint"]]
        for solution in v:
            if solution["ie"]:
                if any(solution["effect"] <= c[0] and solution["effect"]/solution["cost"] < c[1] for c in cutoffs_ie):
                    continue
            if solution["anoint"]:
                if any(solution["effect"] <= c[0] and solution["effect"]/solution["cost"] < c[1] for c in cutoffs_anoints):
                    continue
            if not solution["anoint"] and not solution["ie"]:
                if any(solution["effect"] <= c[0] and solution["effect"]/solution["cost"] < c[1] for c in cutoffs):
                    continue

            solutions.append(solution)

            
    # for s in solutions:
    #     print((s["type"],s["seed"],s["slot"], s["effect"], s["cost"], s["ie"], s["anoint"]))


    with open("data/steiner_solutions.json", "w") as file:
        file.write(json.dumps(solutions, separators=(',', ':')))





if __name__ == '__main__':
    # get_passives_in_radius_of_jewel_slots()
    # get_passives_in_radius_of_keystones()
    # get_timeless_node_mapping()
    fetch_solutions()
    clean_up_data()
