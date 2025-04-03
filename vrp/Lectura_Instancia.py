import re
class VRPFileReader:
    @staticmethod
    def read_vrp_file(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        data = {}
        section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("DIMENSION"):
                data['dimension'] = int(line.split()[-1])
            elif line.startswith("CAPACITY"):
                data['capacity'] = int(line.split()[-1])
            elif line.startswith("NODE_COORD_SECTION"):
                section = 'coordinates'
                data['coordinates'] = []
            elif line.startswith("DEMAND_SECTION"):
                section = 'demands'
                data['demands'] = []
            elif line.startswith("DEPOT_SECTION"):
                section = 'depot'
                data['depot'] = []
            elif section == 'coordinates':
                if line == "EOF":
                    section = None
                else:
                    parts = line.split()
                    data['coordinates'].append((int(parts[0]), float(parts[1]), float(parts[2])))
            elif section == 'demands':
                if line == "EOF":
                    section = None
                else:
                    parts = line.split()
                    data['demands'].append(int(parts[1]))
            elif section == 'depot':
                if line == "EOF":
                    section = None
                else:
                    data['depot'].append(int(line))
            elif line.startswith("NAME"):
                data['name'] = line.split()[-1]
        
        return data

    @staticmethod
    def read_sol_file(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        solution = []
        total_cost = 0
        for line in lines:
            line = line.strip()
            if line.startswith("Route"):
                parts = re.findall(r'\d+', line)
                route = list(map(int, parts[1:]))
                solution.append(route)
            elif line.startswith("Cost"):
                total_cost = float(line.split()[-1])
        
        return solution, total_cost