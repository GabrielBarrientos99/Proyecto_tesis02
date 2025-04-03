import random
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from .Lectura_Instancia import VRPFileReader

class Nodo:
    def __init__(self, id, x, y, demanda):
        self.id = id
        self.x = x
        self.y = y
        self.demanda = demanda

class Deposito(Nodo):
    def __init__(self, x, y, k, Q):
        super().__init__(0, x, y, 0)
        self.k = k
        self.Q = Q

class CVRP:
    def __init__(self, num_clientes=None, max_demanda=None, max_x=None, max_y=None, k=None, Q=None, file_path=None, file_save=None):
        if file_path:
            self.load_instance(file_path)
            self.file_save = file_save
            self.filepath = file_path
        else:
            self.num_clientes = num_clientes
            self.deposito = Deposito(0, 0, k, Q)            
            self.clientes = self.generar_clientes(num_clientes, max_demanda, max_x, max_y, Q)
            self.matriz_distancias = self.calcular_matriz_distancias()
            self.demandas = [cliente.demanda for cliente in self.clientes]
            self.file_save = file_save
            self.model_name = 'CVRP_random'

    def load_instance(self, file_path):
        data = VRPFileReader.read_vrp_file(file_path)
        self.model_name = data['name']
        self.num_clientes = data['dimension'] - 1
        self.deposito = Deposito(data['coordinates'][0][1], data['coordinates'][0][2], len(data['coordinates']) - 1, data['capacity'])
        self.demandas = data['demands'][1:]
        self.clientes = [Nodo(i, x, y, self.demandas[i - 1]) for i, (_, x, y) in enumerate(data['coordinates'][1:], start=1)]
        self.matriz_distancias = self.calcular_matriz_distancias_from_coords(data['coordinates'][1:])

    def generar_clientes(self, num_clientes, max_demanda, max_x, max_y, Q):
        clientes = []
        for i in range(1, self.num_clientes + 1):
            x = random.uniform(-max_x, max_x)
            y = random.uniform(-max_y, max_y)
            demanda = random.randint(1, max_demanda)
            while demanda >= Q:
                demanda = random.randint(1, max_demanda)
            clientes.append(Nodo(i, x, y, demanda))
        return clientes

    def calcular_matriz_distancias_from_coords(self, coords):
        coords_with_depot = [(self.deposito.id, self.deposito.x, self.deposito.y)] + coords
        n = len(coords_with_depot)
        matriz = np.zeros((n, n), dtype=float) 

        for i, coord1 in enumerate(coords_with_depot):
            for j, coord2 in enumerate(coords_with_depot):
                distancia = math.sqrt((coord1[1] - coord2[1]) ** 2 + (coord1[2] - coord2[2]) ** 2)
                matriz[i][j] = float(distancia)

        return matriz

    def calcular_matriz_distancias(self):
        nodos = [self.deposito] + self.clientes
        matriz = np.zeros((len(nodos), len(nodos)),dtype=float)
        for nodo1 in nodos:            
            for nodo2 in nodos:
                distancia = math.sqrt((nodo1.x - nodo2.x) ** 2 + (nodo1.y - nodo2.y) ** 2)
                matriz[nodo1.id][nodo2.id] = float(distancia)
      
        return matriz

    def calcular_costo_total(self, rutas):
        total_cost = 0
        for ruta in rutas:
            ruta_completa = [0] + ruta + [0]
            for i in range(len(ruta_completa) - 1):
                nodo1 = ruta_completa[i]
                nodo2 = ruta_completa[i + 1]
                total_cost += self.matriz_distancias[nodo1][nodo2]
        return total_cost
    
    def get_solution(self,file_path_solution):
            sol,_= VRPFileReader.read_sol_file(file_path_solution)
            return self.calcular_costo_total(sol)

    def graficar(self, rutas=None):
        num_clientes = len(self.clientes)
        if num_clientes > 25:
            fig, ax = plt.subplots(figsize=(20, 10))
        else:
            fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(self.deposito.x, self.deposito.y, c='red', marker='X', s=100, label='Depósito')
        x_coords = [cliente.x for cliente in self.clientes]
        y_coords = [cliente.y for cliente in self.clientes]
        labels = [cliente.id for cliente in self.clientes]
        demands = [cliente.demanda for cliente in self.clientes]

        ax.scatter(x_coords, y_coords, c='blue', marker='o', s=50, label='Clientes')
        ax.annotate('0', (self.deposito.x, self.deposito.y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=12, weight='bold')

        for i, (x, y, label, demand) in enumerate(zip(x_coords, y_coords, labels, demands)):
            ax.annotate(label, (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, weight='bold')
            if num_clientes > 25:
                ax.annotate(f'{demand}', (x, y), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=10, color='green')
            else:
                ax.annotate(f'Demanda: {demand}', (x, y), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=10, color='green')

        if rutas:
            colors = cm.rainbow(np.linspace(0, 1, len(rutas)))
            for idx, ruta in enumerate(rutas):
                ruta_completa = [0] + ruta + [0]
                for i in range(len(ruta_completa) - 1):
                    nodo1 = self.deposito if ruta_completa[i] == 0 else self.clientes[ruta_completa[i] - 1]
                    nodo2 = self.deposito if ruta_completa[i + 1] == 0 else self.clientes[ruta_completa[i + 1] - 1]
                    ax.plot([nodo1.x, nodo2.x], [nodo1.y, nodo2.y], color=colors[idx], label=f'Ruta {idx + 1}' if i == 0 else "")

        handles, labels = ax.get_legend_handles_labels()
        route_legend = [handle for handle, label in zip(handles, labels) if 'Ruta' in label]
        ax.legend(handles=route_legend, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)

        if rutas:
            total_cost = self.calcular_costo_total(rutas)
            ax.set_title(f'CVRP - Costo Total = {total_cost:.2f}', fontsize=16, fontweight='medium', color='black')
        else:
            ax.set_title('CVRP', fontsize=12, fontweight='bold')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid()
        if self.file_save:
            #print(f'Guardando imagen...:{self.file_save}')
            plt.savefig(self.file_save)
        #plt.show()
