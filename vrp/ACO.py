import numpy as np
from .Problema_CVRP import CVRP
from .Algoritmo_Genetico_CVRP import Optimizer
import matplotlib.pyplot as plt

class Ant:
    def __init__(self, indice):
        self.indice = indice
        self.solution = []
        self.count = 0
        self.cost_solution = float('inf')

class AntColonyOptimizer_v2:
    def __init__(self, cvrp, num_ants, max_iter=500, max_count=20, alpha=5.0, beta=5.0, evaporation_rate=0.1, pheromone_initial=1.0, elitist_factor=6, max_r=20, verbose=False):
        # Inicialización de parámetros
        self.cvrp = cvrp
        self.num_ants = num_ants
        self.ants = [Ant(i) for i in range(self.num_ants)]
        self.max_iter = max_iter
        self.max_count = max_count
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.pheromone_matrix = np.full((cvrp.num_clientes + 1, cvrp.num_clientes + 1), pheromone_initial)
        self.elitist_factor = elitist_factor
        self.max_r = max_r
        self.verbose = verbose

        # Almacena la mejor solución global
        self.best_global_solution = None
        self.best_global_cost = float('inf')

        self.optimizer = Optimizer(cvrp.matriz_distancias)

    def get_solution(self, count):
        """Construye una solución para una hormiga en forma de lista de rutas sin incluir el nodo de depósito explícitamente."""
        solution = []
        current_route = []
        q_actual = self.cvrp.deposito.Q
        visited = set()
        current_node = 0

        while len(visited) < self.cvrp.num_clientes:
            next_node = self.select_next_node(current_node, visited, q_actual, count)

            if next_node is None:
                if current_route:
                    solution.append(current_route)
                current_route = []
                q_actual = self.cvrp.deposito.Q
                current_node = 0
                continue

            current_route.append(next_node)
            visited.add(next_node)
            q_actual -= self.cvrp.demandas[next_node - 1]
            current_node = next_node

        if current_route:
            solution.append(current_route)

        return solution

    def select_next_node(self, current_node, visited, q_actual, count):
        """Selecciona el siguiente nodo de entre los más cercanos no visitados que cumplan la restricción de capacidad."""
        temp_alpha = self.alpha / 2 if count > self.max_count // 2 else self.alpha
        temp_beta = self.beta * 1.5 if count > self.max_count // 2 else self.beta
    
        # Ajuste de número de nodos a explorar
        if count > self.max_count // 2:
            n_closest = max(1, min(self.cvrp.num_clientes, (self.cvrp.num_clientes // 4) + count))
        else:
            n_closest = max(1, self.cvrp.num_clientes // 4)
    
        unvisited_nodes = [(node, self.cvrp.matriz_distancias[current_node][node]) 
                           for node in range(1, self.cvrp.num_clientes + 1) 
                           if node not in visited and self.cvrp.demandas[node - 1] <= q_actual]
    
        if not unvisited_nodes:
            return None
        
        unvisited_nodes.sort(key=lambda x: x[1])
        closest_unvisited = [node for node, _ in unvisited_nodes[:n_closest]]
    
        probabilities = []
        for node in closest_unvisited:
            pheromone = self.pheromone_matrix[current_node][node] ** temp_alpha
    
            # Evita divisiones por cero en `visibility` al escalar distancias
            distancia = self.cvrp.matriz_distancias[current_node][node]
            if distancia > 0:  # Asegura que distancia no sea cero
                scaled_distance = distancia / max(1, np.max(self.cvrp.matriz_distancias))  # Método 1 con control de cero
                visibility = (1.0 / scaled_distance) ** temp_beta  # Método 1
                probabilities.append(pheromone * visibility)
            else:
                probabilities.append(0)  # Si la distancia es cero, no contribuye a la visibilidad
    
        probabilities = np.array(probabilities)
    
        # Normalización con control adicional para evitar NaN o infinito
        if probabilities.sum() > 0 and not np.isnan(probabilities).any():
            probabilities /= probabilities.sum()
        else:
            # Si todas las probabilidades son cero, asigna una probabilidad uniforme
            probabilities = np.ones(len(probabilities)) / len(probabilities)
    
        return np.random.choice(closest_unvisited, p=probabilities)

    def update_pheromones(self):
        """Actualiza las feromonas en la matriz de acuerdo con las soluciones encontradas por las hormigas."""
        self.pheromone_matrix *= (1 - self.evaporation_rate)

        for ant in self.ants:
            solution = ant.solution
            cost = ant.cost_solution
            if cost == 0:
                continue

            # Calcula un factor elitista adaptativo para diversificación de rutas
            adaptive_elitist_factor = self.elitist_factor * (1 + abs(cost - self.best_global_cost) / self.best_global_cost)

            for route in solution:
                for i in range(len(route)):
                    if i == 0:
                        self.pheromone_matrix[0][route[i]] += adaptive_elitist_factor / cost
                    else:
                        self.pheromone_matrix[route[i - 1]][route[i]] += adaptive_elitist_factor / cost
                    self.pheromone_matrix[route[i]][0] += adaptive_elitist_factor / cost

            # Evaporación extra en rutas ineficientes
            if ant.count > self.max_count // 2:
                for route in ant.solution:
                    for i in range(len(route) - 1):
                        self.pheromone_matrix[route[i]][route[i+1]] *= (1 - self.evaporation_rate * 1.5)

    def train(self):
        """Ejecuta el ciclo de entrenamiento del algoritmo ACO."""
        for i in range(self.max_iter):
            for ant in self.ants:
                # Genera y optimiza una solución para la hormiga
                new_solution = self.get_solution(ant.count)
                
                # Aplicar 2-opt y Swap Node para optimización local
                final_solution = self.optimizer.routes_2opt(new_solution)
                final_solution = self.optimizer.swap_nodes(final_solution)
                
                cost_s = self.cvrp.calcular_costo_total(final_solution)

                # Actualiza la mejor solución de la hormiga si mejora
                if cost_s < ant.cost_solution:
                    ant.cost_solution = cost_s
                    ant.solution = final_solution
                    ant.count = 0
                else:
                    ant.count += 1

                # Reinicio de la hormiga con perturbación si no mejora tras `max_count`
                if ant.count > self.max_count:
                    perturbed_solution = self.optimizer.swap_nodes(ant.solution)
                    ant.solution = perturbed_solution
                    ant.cost_solution = self.cvrp.calcular_costo_total(perturbed_solution)
                    ant.count = 0

                # Actualiza la mejor solución global si es mejor que la anterior
                if cost_s < self.best_global_cost:
                    self.best_global_cost = cost_s
                    self.best_global_solution = final_solution

            # Actualización de feromonas al final de cada iteración
            self.update_pheromones()

        # Retorna la mejor solución global y su costo
        return self.best_global_solution, self.best_global_cost