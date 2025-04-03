# Pruebas_generator.py
from vrp.Lectura_Instancia import VRPFileReader
from vrp.Problema_CVRP import CVRP
from django.conf import settings
import os

class Image_Controler(VRPFileReader):
    def __init__(self):
        super().__init__()
        self.BASE_DIR_IMAGE = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'imagenes_pruebas')
        self.BASE_DIR_INSTANCIAS = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias')
        self.json_data = {}
        self.cvrp = None
        self.params_ag = [{
            'population_size': 50,
            'num_generations': 5000,
            'mutation_rate': 0.02,
            'use_elitism': True,
            'gready': False,
            'homogenia': False
        },
        {
            'population_size': 100,
            'num_generations': 1200,
            'mutation_rate': 0.03,
            'use_elitism': True,
            'gready': True,
            'homogenia': True
        },
        {
            'population_size': 300,
            'num_generations': 2000,
            'mutation_rate': 0.01,
            'use_elitism': True,
            'gready': True,
            'homogenia': False
        }]
    
    def generate_image_json(self, instancias):
        for instancia in instancias:
            file_path = os.path.join(self.BASE_DIR_INSTANCIAS, instancia)
            filename = os.path.basename(instancia).replace('.vrp','')
            save_path = os.path.join(self.BASE_DIR_IMAGE, 'instancia', f'{filename}.png')
            self.cvrp = CVRP(file_path=file_path, file_save=save_path)
            self.cvrp.graficar()

            # Guardamos la instancia solucion
            solution_file_path = file_path.replace('.vrp', '.sol')
            routes_solution, cost_sol = VRPFileReader.read_sol_file(solution_file_path)
            solution_graph_file_path = os.path.join(self.BASE_DIR_IMAGE, 'solucion', f'{filename}_sol.png')
            self.cvrp.file_save = solution_graph_file_path
            self.cvrp.graficar(routes_solution)

            # Rellenamos el json
            self.json_data[instancia] = {
                'name': instancia,
                'graph_path': save_path,
                'solution_path': solution_graph_file_path,
                'cost_sol': cost_sol,
                'params_ag': self.params_ag
            }
        return self.json_data

# Creamos una lista de instancias
#list_instancias = ['A/A-n80-k10.vrp', 'A/A-n54-k7.vrp']

#ic = Image_Controler()
#json_data = ic.generate_image_json(list_instancias)
