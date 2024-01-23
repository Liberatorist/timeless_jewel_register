from collections import defaultdict
from copy import deepcopy
from enum import Enum
import io
import itertools
import os, stat
import json
import math
from time import time
import zipfile
from steiner_solver.steiner_interface import SteinerSolver




def get_passives_needed(jewel_id: int, anchor_points: set[int], aura_effect_nodes: set[int]) -> list[int]:
    terminals = [jewel_id] + list(anchor_points) + list(aura_effect_nodes)
    solver = SteinerSolver()
    steiner_nodes = solver.get_steiner_tree_for_terminals(terminals)
    return steiner_nodes


with open("data/jewel_slots.json", "r") as file:
    jewel_slots = json.loads(file.read())
with open("data/in_radius_of_jewel.json", "r") as file:
    in_jewel_radius = {int(k): set(v) for k, v in json.loads(file.read()).items()}


with open("data/in_radius_of_keystone.json", "r") as file:
    passives_for_keystone = {int(k): set(v) for k, v in json.loads(file.read()).items()}

with open("data/in_radius_of_thread.json", "r") as file:
    passives_for_thread = {k: {int(vk): set(vv) for vk, vv in v.items()} for k, v in json.loads(file.read()).items()}

with open("data/aura_nodes_by_seed.json", "r") as file:
    aura_nodes_by_seed = json.loads(file.read())

with open("static/tree.json", "r") as file:
    tree = {int(k): v for k, v in json.loads(file.read()).items()}

with open("data/tree_data.json", "r") as file:
    tree_data = json.loads(file.read())["nodes"]
    del tree_data["root"]

with open("data/thread_of_hope_overlaps.json", "r") as file:
    threads_for_jewel = {int(k): v for k, v in json.loads(file.read()).items()}


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

def get_timeless_node_mapping():
    data={}
    for jewel_type in [TimelessJewelType.BRUTAL_RESTRAINT, TimelessJewelType.ELEGANT_HUBRIS, TimelessJewelType.GLORIOUS_VANITY]:
        print("Now mapping", jewel_type)
        data[jewel_type.value] = {}
        with open(f'data/TimelessJewels/{jewel_type.value.lower().replace(" ", "_")}_passives.txt', 'r', encoding='utf8') as file:
            passives = [int(line) for line in file.read().split('\n') if line != '']

        with open("one_time_use/steiner_solver/node_mapping.json", "r") as file:
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
                            continue
                        for apk, apv in zip(ap[1::2], ap[2::2]):
                            if apk=="3835":
                                nodes.append(p)
                                values.append(int(apv))
                    data[jewel_type.value][seed] = [nodes, values]

    with open("data/aura_nodes_by_seed.json", "w") as file:
        file.write(json.dumps(data, separators=(',', ':')))



notable_hashes_for_jewels = [
	26725, 36634, 33989, 41263, 60735, 61834, 31683, 28475, 6230, 48768, 34483, 7960,
	46882, 55190, 61419, 2491, 54127, 32763, 26196, 33631, 21984, 29712, 48679, 9408,
	12613, 16218, 2311, 22994, 40400, 46393, 61305, 12161, 3109, 49080, 17219, 44169,
	24970, 36931, 14993, 10532, 23756, 46519, 23984, 51198, 61666, 6910, 49684, 33753,
	18436, 11150, 22748, 64583, 61288, 13170, 9797, 41876, 59585,
]

def in_radius(node_id1: int, node_id2: int, radius: int):
    return (tree[node_id1]["x"]  - tree[node_id2]["x"]) ** 2 +\
            (tree[node_id1]["y"]  - tree[node_id2]["y"]) ** 2 <= radius**2

def in_between(node_id1: int, node_id2: int, radii: dict):
    return radii["min"] ** 2 <= (tree[node_id1]["x"]  - tree[node_id2]["x"]) ** 2 +\
            (tree[node_id1]["y"]  - tree[node_id2]["y"]) ** 2 <= radii["max"]**2


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

thread_of_hope_radii = {
    "small": {"min": 960, "max": 1320},
    "medium": {"min": 1320, "max": 1680},
    "large": {"min": 1680 , "max": 2040},
    "very_large": {"min": 2040, "max": 2400},
    "massive": {"min": 2400, "max": 2880},
}

def get_relevant_threads_of_hope():
    data = {}
    for jewel_id in notable_hashes_for_jewels:
        if jewel_id not in tree:
            continue
        data[jewel_id] = []
        nodes_in_radius = in_jewel_radius[jewel_id]
        for thread_id in notable_hashes_for_jewels:
            if thread_id not in tree or  jewel_id not in tree or thread_id == jewel_id:
                continue
            for size in ["small", "medium", "large", "very_large", "massive"]:
                overlap = nodes_in_radius & passives_for_thread[size][thread_id]
                if overlap:
                    data[jewel_id].append({"size": size, "thread_id": thread_id})

    with open("data/thread_of_hope_overlaps.json", "w") as file:
        file.write(json.dumps(data, separators=(',', ':')))

def get_passives_in_thread_of_hope_range():
    data = {"small": {}, "medium": {}, "large": {}, "very_large": {}, "massive": {} }
    for thread_id in notable_hashes_for_jewels:
        if thread_id not in tree:
            continue
        for thread_size, radii in thread_of_hope_radii.items():
            data[thread_size][thread_id] = []
            for node_id, node in tree.items():
                if node["type"] in ["notable", "small"] and in_between(node_id, thread_id, radii):
                    data[thread_size][thread_id].append(int(node_id))
    with open("data/in_radius_of_thread.json", "w") as file:
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


def get_cost(nodes: set[int], jewel_type: TimelessJewelType, slot: int):
    if "exact_cost" in jewel_slots[jewel_type.value][slot]:
        return jewel_slots[jewel_type.value][slot]["exact_cost"]
    else:
        return len(nodes) - jewel_slots[jewel_type.value][slot]['normal_pathing_cost']

def find_solution_without_anoint(seed, jewel_type, jewel_id, slot, aura_nodes, effect):
    steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=jewel_slots[jewel_type.value][slot]["anchors"], aura_effect_nodes=aura_nodes)
    return {
        "seed": seed,
        "type": jewel_type.value,
        "slot": slot,
        "steiner_tree": steiner_tree_nodes,
        "aura_nodes": list(aura_nodes),
        "cost": get_cost(steiner_tree_nodes, jewel_type, slot),
        "effect": effect,
        "anoint": 0,
        "ie": 0,
        "thread": {}
    }

def find_solutions_with_anoint(seed: int, jewel_type: TimelessJewelType, jewel_id: int, slot: int, aura_nodes: list[int], effect: int):
    solutions = []
    for node in aura_nodes:
        anoint_nodes = set(aura_nodes) - {node}
        steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=jewel_slots[jewel_type.value][slot]["anchors"], aura_effect_nodes=anoint_nodes)
        cost = get_cost(steiner_tree_nodes, jewel_type, slot)
        steiner_tree_nodes.append(node)
        solutions.append({
            "seed": seed,
            "type": jewel_type.value,
            "slot": slot,
            "steiner_tree": steiner_tree_nodes,
            "aura_nodes": list(aura_nodes),
            "cost": cost,
            "anoint": node,
            "ie": 0,
            "thread": {},
            "effect": effect
        })
    return solutions



def find_solutions_with_ie(seed: int, jewel_type: TimelessJewelType, jewel_id: int, slot: int, aura_nodes: list[int], effect: int, cost_without_ie: int, anoint: int=None):
    solutions = []
    aura_nodes = set(aura_nodes) - {anoint} if anoint else set(aura_nodes)
    for keystone_id, passives_around_keystone in passives_for_keystone.items():
        if len(set(aura_nodes) & passives_around_keystone) >= 1:
            remaining_nodes = set(aura_nodes) - passives_around_keystone
            steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=jewel_slots[jewel_type.value][slot]["anchors"], aura_effect_nodes=remaining_nodes)
            steiner_tree_nodes += list(set(aura_nodes) & passives_around_keystone)
            cost = get_cost(steiner_tree_nodes, jewel_type, slot)
            if cost_without_ie - cost < 2:  # impossible escape has to save at least 2 points
                continue
            solutions.append({
                "seed": seed,
                "type": jewel_type.value,
                "slot": slot,
                "steiner_tree": steiner_tree_nodes if not anoint else steiner_tree_nodes + [anoint],
                "aura_nodes": list(aura_nodes) if not anoint else list(aura_nodes) + [anoint],
                "cost": cost,
                "anoint": anoint if anoint else 0,
                "ie": keystone_id,
                "thread": {},
                "effect": effect
            })
    return solutions

def find_solutions_with_thread(seed: int, jewel_type: TimelessJewelType, jewel_id: int, slot: int, aura_nodes: list[int], effect: int, anoint: int=None):
    solutions = []
    aura_nodes = set(aura_nodes) - {anoint} if anoint else set(aura_nodes)
    for thread in threads_for_jewel[jewel_id]:
            passives_in_thread = passives_for_thread[thread["size"]][thread["thread_id"]]
            thread_nodes = set(passives_in_thread) & aura_nodes
            if len(thread_nodes) >= 2:
                remaining_nodes = set(aura_nodes) - passives_in_thread
                anchor_points=jewel_slots[jewel_type.value][slot]["anchors"] + [thread["thread_id"]]
                steiner_tree_nodes = get_passives_needed(jewel_id=jewel_id, anchor_points=anchor_points , aura_effect_nodes=remaining_nodes)
                steiner_tree_nodes += list(thread_nodes)
                cost = get_cost(steiner_tree_nodes, jewel_type, slot)
                solutions.append({
                    "seed": seed,
                    "type": jewel_type.value,
                    "slot": slot,
                    "steiner_tree": steiner_tree_nodes,
                    "aura_nodes": list(aura_nodes) if not anoint else list(aura_nodes) + [anoint],
                    "cost": cost,
                    "anoint": 0 if not anoint else anoint,
                    "ie": 0,
                    "thread": {"size": thread["size"], "thread_id": thread["thread_id"]},
                    "effect": effect
                })
                if effect >= 36 and effect/cost >= 3.5 and thread["size"] != "massive":
                    print(solutions[-1])
    return solutions

def iteratively_cull_nodes(nodes: list[int], effects: list[int], min_effect: int):
    yield nodes, effects
    for node, effect in zip(nodes, effects):
        culled_nodes = [n for n in nodes if n!=node]
        culled_effects = [e for e in effects if e!=effect]
        if sum(culled_effects) < min_effect:
            continue
        for n, e in iteratively_cull_nodes(culled_nodes, culled_effects, min_effect):
            yield n, e

def get_worthwhile_passive_combinations(nodes: list[int], effects: list[int], min_effect: int):
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
            passives_in_radius = deepcopy(in_jewel_radius[jewel_id])
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
                    for aura_nodes, effect_values in get_worthwhile_passive_combinations(aura_nodes, effect_values, min_effect[jewel_type]):
                        effect = sum(effect_values)
                        solution_without_anoint = find_solution_without_anoint(seed, jewel_type, jewel_id, slot, aura_nodes, effect)
                        solutions.append(solution_without_anoint)
                        cost = solution_without_anoint["cost"]
                        if jewel_type == TimelessJewelType.BRUTAL_RESTRAINT:
                            continue
                        solutions += find_solutions_with_ie(seed, jewel_type, jewel_id, slot, aura_nodes, effect, cost)

                        solutions += find_solutions_with_thread(seed, jewel_type, jewel_id, slot, aura_nodes, effect)

                        if effect >= 36:
                            solutions_with_anoint = find_solutions_with_anoint(seed, jewel_type, jewel_id, slot, aura_nodes, effect)
                            solutions += solutions_with_anoint
                            for solution in solutions_with_anoint:
                                solutions += find_solutions_with_ie(seed, jewel_type, jewel_id, slot, aura_nodes, effect, solution["cost"], solution["anoint"])
                                solutions += find_solutions_with_thread(seed, jewel_type, jewel_id, slot, aura_nodes, effect, solution["anoint"])


    with open("data/steiner_solutions.json", "w") as file:
        file.write(json.dumps(solutions, separators=(',', ':')))
    print(time()-t)


def get_cutoff(solution):
    if solution["cost"] != 0:
        return (solution["effect"], solution["effect"]/solution["cost"])
    else:
        return (solution["effect"], 999)
    

def solution_has(solution, anoint, ie, thread):
    return ((anoint and solution["anoint"]) or (not anoint and not solution["anoint"])) and\
            ((ie and solution["ie"]) or (not ie and not solution["ie"])) and\
            ((thread and solution["thread"]) or (not thread and not solution["thread"]))

def clean_up_data():
    with open("data/steiner_solutions.json", "r") as file:
        data = json.loads(file.read())
    combinations = list(itertools.product(*[[True, False]]*3))

    data_dict = {}
    for solution in data:
        key = (solution["type"],solution["seed"],solution["slot"])
        if key not in data_dict:
            data_dict[key] = []
        data_dict[key].append(solution)

    solutions = []
    for k, v in data_dict.items():
        previous_solutions = []
        cutoffs = {c: [] for c in combinations}

        for anoint, ie, thread in combinations:
            for solution in v:
                if solution_has(solution, anoint, ie, thread):
                    cutoffs[(anoint, ie, thread)].append(get_cutoff(solution))

        for solution in v:
            cutoff = get_cutoff(solution)
            for anoint, ie, thread in combinations:
                if solution_has(solution, anoint, ie, thread) and not any(cutoff[0] <= c[0] and cutoff[1] < c[1] for c in cutoffs[(anoint, ie, thread)]) and not cutoff in previous_solutions:
                    solutions.append(solution)
                    previous_solutions.append(cutoff)


    with open("data/jewel_slots.json", "r") as file:
        jewels = json.loads(file.read())

    all_slots = set()
    for v in jewels.values():
        for slot_name in v.keys():
            all_slots.add(slot_name)
    

    keys = ["seed", "type", "effect", "slot", "active_nodes", "aura_nodes", "cost", "anoint", "ie", "thread"]
    num2type = ["Brutal Restraint", "Glorious Vanity", "Elegant Hubris"]
    type2num = {v:k for k,v in enumerate(num2type)}
    num2slot = sorted(all_slots)
    slot2num = {k: v for v, k in enumerate(num2slot)}

 
    compressed_solutions = {}
    compressed_solutions["num2slot"] = num2slot
    compressed_solutions["num2type"] = num2type
    compressed_solutions["keys"] = keys
    compressed_solutions["solutions"] = []

    for s in solutions:
        compressed_solutions["solutions"].append(
            [s["seed"], type2num[s["type"]], s["effect"], slot2num[s["slot"]], s["steiner_tree"], s["aura_nodes"], s["cost"], s["anoint"],  s["ie"], s["thread"] if s["thread"] else {}]
        )
        
    with open("static/compressed_solutions.json", "w") as file:
        file.write(json.dumps(compressed_solutions, separators=(',', ':')))


def setup_steiner_solver():
    with open("one_time_use/steiner_solver/node_mapping.json", "r") as file:
        node_mapping = json.loads(file.read())
    stp_string = ""
    node_count = 0
    edge_count = 0
    for node_id, node in tree_data.items():
        if str(node_id) not in node_mapping:
            continue
        node_count += 1
        for neighbour in node["in"]:
            if neighbour not in node_mapping:
                continue
            stp_string += f"E {node_mapping[neighbour]} {node_mapping[str(node_id)]} 1\n"
            edge_count += 1
    stp_string = f"33D32945 STP File, STP Format Version 1.0\nSECTION Graph\nNodes {node_count}\nEdges {edge_count}\n{stp_string}END\n"
    with open("one_time_use/steiner_solver/base.stp", "w") as file:
        file.write(stp_string)
    
    with open("one_time_use/steiner_solver/node_mapping", "w") as file:
        values = [0] * len(node_mapping)
        for k, v in node_mapping.items():
            values[v] = str(k)
        file.write("\n".join(values))



         


if __name__ == '__main__':
    # get_passives_in_radius_of_jewel_slots()
    # get_passives_in_radius_of_keystones()
    # get_timeless_node_mapping()
    # get_relevant_threads_of_hope()
    # fetch_solutions()
    clean_up_data()
    # setup_steiner_solver()
