import json


with open("data/steiner_solutions.json", "r") as file:
    solutions = json.loads(file.read())

with open("data/jewel_slots.json", "r") as file:
    jewels = json.loads(file.read())

all_slots = set()
for k, v in jewels.items():
    for vv in v.keys():
        all_slots.add(vv)

keys = ["seed", "type", "effect", "slot", "active_nodes", "aura_nodes", "cost", "anoint", "ie"]
num2type = ["Brutal Restraint", "Glorious Vanity", "Elegant Hubris"]
type2num = {v:k for k,v in enumerate(num2type)}
num2slot = list(all_slots)
slot2num = {k: v for v, k in enumerate(num2slot)}


compressed_solutions = {}
compressed_solutions["num2slot"] = num2slot
compressed_solutions["num2type"] = num2type
compressed_solutions["keys"] = keys
compressed_solutions["solutions"] = []

for s in solutions:

    compressed_solutions["solutions"].append(
        [s["seed"], type2num[s["type"]], s["effect"], slot2num[s["slot"]], s["steiner_tree"], s["aura_nodes"], s["cost"], s["anoint"][0] if s["anoint"] else 0,  s["ie"][0] if s["ie"] else 0]
    )
    
with open("data/compressed_solutions.json", "w") as file:
    file.write(json.dumps(compressed_solutions, separators=(',', ':')))


