import json
import os
import subprocess


class SteinerSolver:
    def __init__(self):
        self.steiner_dir = os.path.join(os.getcwd(), "one_time_use", "steiner_solver")
        with open(os.path.join(self.steiner_dir, "base.stp"), "r") as file:
            self.base_string = file.read()
        with open(os.path.join(self.steiner_dir, "node_mapping"), "r") as file:
            self.denormalize = [int(node_id) for node_id in file.read().split("\n")]
        self.normalize = {int(node_id): mapping_id for mapping_id, node_id in enumerate(self.denormalize)}

    def get_steiner_tree_for_terminals(self, terminals: list[int]) -> list[int]:
        full_string = self.base_string +\
                      f"SECTION Terminals\nTerminals {len(terminals)}\n" +\
                      "\n".join('T ' + str(self.normalize[t]) for t in terminals) +\
                      "\nEND\nEOF"

        with open(os.path.join(self.steiner_dir, "x.stp"), "w") as file:
            file.write(full_string)
        solver_location = os.path.join(self.steiner_dir, "stp.linux.x86_64.gnu.opt.spx2")
        file_name = os.path.join(self.steiner_dir, "x.stp")
        settings = os.path.join(self.steiner_dir, "settings", "write.set")
        command = f"{solver_location} -f {file_name} -s {settings}"
        subprocess.run(command, shell=True, capture_output=True)
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
