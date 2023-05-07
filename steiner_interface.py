import json
import subprocess
from time import time


class SteinerSolver:
    def __init__(self):
        with open("steiner_solver/base.stp", "r") as file:
            self.base_string = file.read()
        with open("steiner_solver/node_mapping.json", "r") as file:
            self.normalize = {int(k): v for k, v in json.loads(file.read()).items()}
        self.denormalize = {v: k for k, v in self.normalize.items()}
    def get_steiner_tree_for_terminals(self, terminals: list[int]) -> list[int]:
        full_string = self.base_string +\
                      f"SECTION Terminals\nTerminals {len(terminals)}\n" +\
                      "\n".join('T ' + str(self.normalize[t]) for t in terminals) +\
                      "\nEND\nEOF"

        with open("steiner_solver/x.stp", "w") as file:
            file.write(full_string)
        subprocess.call("./steiner_solver/stp.linux.x86_64.gnu.opt.spx2 -f steiner_solver/x.stp -s steiner_solver/settings/write.set", shell=True, stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        steiner_nodes = []
        with open("x.stplog") as file:
            
            lines = file.read().split("\n")
            for idx, line in enumerate(lines):
                if line.startswith("Vertices"):
                    for vertex_line in lines[idx + 1:]:
                        if vertex_line.startswith("Edges"):
                            return steiner_nodes
                        steiner_nodes.append(self.denormalize[int(vertex_line.split(" ")[1])])
        return steiner_nodes


