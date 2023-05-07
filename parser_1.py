import json


with open("data/steiner_solutions.json", "r") as file:
    data = json.loads(file.read())

for solution in data:
    if solution["ie"]:
        solution["cost"] += 1
    if solution["anoint"]:
        solution["cost"] -= 1

with open("data/steiner_solutions.json", "w") as file:
    file.write(json.dumps(data, separators=(',', ':')))