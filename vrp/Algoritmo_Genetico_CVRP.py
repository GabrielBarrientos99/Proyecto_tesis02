#!/usr/bin/env python
# coding: utf-8

## Algoritmo genetico

import numpy as np
import random
import matplotlib.pyplot as plt

# In[3]:


class Fitness:
    """
    Clase para calcular y almacenar la aptitud (fitness) de una población en el CVRP.

    Atributos:
        distance_matrix (list of list of float): Matriz de distancias entre cada par de clientes.
        demands (list of int): Lista de demandas de cada cliente.
        vehicle_capacity (int): Capacidad máxima de cada vehículo.
        fitness_values (list of float): Lista de valores de fitness de la población.
        normalized_fitness (list of float): Lista de valores de fitness normalizados.
        total_costs (list of float): Lista de costos totales de cada individuo.
    """
    def __init__(self, distance_matrix, demands, vehicle_capacity):
        self.distance_matrix = distance_matrix
        self.demands = demands
        self.vehicle_capacity = vehicle_capacity
        self.fitness_values = []
        self.normalized_fitness = []
        self.total_costs = []
        self.population = []
        # Seleccionar mejor individuo
        self.best_individuo = None
        self.best_routes = None
        self.best_total_cost = None

    def calculate_route_cost(self, route):
        """Calcula el costo total de una ruta específica basada en una matriz de distancias."""
        cost = 0
        ruta_completa = [0] + route + [0]
        for i in range(len(ruta_completa) - 1):
            cost += self.distance_matrix[ruta_completa[i]][ruta_completa[i + 1]]        
        return cost

    def calculate_total_cost(self,routes):
        total_cost = 0
        for route in routes:
            total_cost += self.calculate_route_cost(route)
        return total_cost
        

    def fitness_function(self, individual):
        """Evalúa la aptitud de una solución individual en el CVRP.

        Args:
            individual (list of int): Representación codificada del individuo.

        Returns:
            float: Valor de fitness del individuo. Un valor más bajo indica una mejor solución.
        """
        # Decodificar el individuo en rutas
        routes = self.decode_individual(individual)
        
        # Calcular el costo total y penalizaciones por sobrecapacidad
        total_cost = self.calculate_total_cost(routes)
        
        self.total_costs.append(total_cost)

        # Invertir el costo para el cálculo del fitness
        if total_cost > 0:
            return 1 / total_cost
        else:
            return float('inf')  # Manejo de división por cero o costos nulos

    def fit(self, population):
        """Calcula y almacena los valores de fitness para la población actual."""
        self.population = population
        self.total_costs = []
        self.fitness_values = [self.fitness_function(ind) for ind in self.population]        
        self.normalize_fitness()

        # Hallamos el mejor individuo
        self.best_individuo = self.population[np.argmax(self.normalized_fitness)]  
        self.best_fitness_ind=self.fitness_values[np.argmax(self.normalized_fitness)] 
        self.best_routes = self.decode_individual(self.best_individuo)
        self.best_total_cost = self.calculate_total_cost(self.best_routes)
        

    def normalize_fitness(self):
        """Normaliza los valores de fitness de la población."""
        total_fitness = sum(self.fitness_values)
        self.normalized_fitness = [f / total_fitness for f in self.fitness_values]

    def decode_individual(self, individual):
        """Decodifica un individuo en una lista de rutas."""
        routes = []
        current_route = []
        current_load = 0
    
        for customer in individual:
            if current_load + self.demands[customer - 1] <= self.vehicle_capacity:
                current_route.append(customer)
                current_load += self.demands[customer - 1]
            else:
                routes.append(current_route)
                current_route = [customer]
                current_load = self.demands[customer - 1]
    
        if current_route:
            routes.append(current_route)
    
        return routes

class Optimizer:
    def __init__(self, matriz_distancia):
        self.d = matriz_distancia

    def algorithm_2opt(self,solution:list)->list:
        ''' Función que aplica a una solución el algoritmo 2-opt para eliminar cruces en un ruta
            Args:
                - solution(list) : una lista de números solucion, que generalmente representa una ruta.
            Return:
                - new_solution(list): la anterior lista sin cruces entre caminos.
        '''
        # Creamos la lista a retornar
        new_solution = solution.copy()
        # Inicializamos nuestra bandera
        change = True
        # Almacenamos la matriz de distancia
        d = self.d
        # Inicializamos el bucle
        while change:
            # Forzamos como que no hay cambios
            change = False
            # Buscamos cada par (i,i+1,j,j+1) que tenga posible cruce
            for i in range(len(solution)-2):
                for j in range(i+2,len(solution)-1):
                    c_actual = d[new_solution[i],new_solution[i+1]] + d[new_solution[j],new_solution[j+1]]
                    c_nuevo =  d[new_solution[i],new_solution[j]] + d[new_solution[i+1],new_solution[j+1]]
                    diff = c_nuevo - c_actual
                    # Si el costo nuevo es menor al actual      
                    if diff < 0 :
                        #print(f'diff:{diff}')
                        # intercambiamos esos valores
                        new_solution[i+1:j+1]=new_solution[i+1:j+1][::-1]
                        # verificar el cambio
                        change = True
        return new_solution

    def routes_2opt(self,routes:list[list])->list[list]:
        new_routes = []
        for r in routes:
            new_route = [0]+r+[0]
            new_routes.append(self.algorithm_2opt(new_route))
        return new_routes   

    def swap_nodes(self, solution):
        """Intenta mejorar la solución intercambiando dos nodos en la ruta y verificando si mejora el costo."""
        improved = True
        while improved:
            improved = False
            for route in solution:
                for i in range(len(route) - 1):
                    for j in range(i + 1, len(route)):
                        # Realizar el intercambio
                        route[i], route[j] = route[j], route[i]
                        
                        # Calcula el nuevo costo con el intercambio
                        new_cost = self.calculate_route_cost(route)
                        
                        # Si el nuevo costo es menor, se conserva; si no, revertimos el cambio
                        if new_cost < self.calculate_route_cost(route):
                            improved = True
                        else:
                            # Revertimos el cambio si no mejora
                            route[i], route[j] = route[j], route[i]
        return solution
        
    def calculate_route_cost(self, route):
        """Calcula el costo de una ruta específica."""
        cost = 0
        for i in range(len(route) - 1):
            cost += self.d[route[i]][route[i + 1]]
        return cost
 

    def __str__(self)->str:
        return f'Clase de optimizadores'

# In[4]:

class GreadyAlgorithm:
    def __init__(self,cvrp):
        self.cvrp = cvrp
        self.num_customers = cvrp.num_clientes
        self.capacity = cvrp.deposito.Q
        self.distances = cvrp.matriz_distancias
        self.nodo_actual = 0
        self.visited = [0] * self.num_customers
        self.demanda_actual = 0

    
    def can_visit(self,cliente):
        cond1 = cliente!=self.nodo_actual
        cond2 = self.visited[cliente-1] < 1
        cond3 = self.demanda_actual + self.cvrp.demandas[cliente-1] <= self.capacity
        return cond1 and cond2 and cond3

    def get_targets(self,clientes):
        return list(filter(self.can_visit,clientes))        

    # Creamos nuestro gready que retorna un individuo solucion
    def get_individual(self):
        
        route = [] # individuo que retornaremos
        # Creamos un buckle
        while not all(self.visited):
            # Obtenemos los clientes que se pueden visitar
            targets = self.get_targets(list(range(1,self.num_customers+1)))
            
            if targets :
                # Obtenemos el target con la minima distancia
                target = min(targets,key=lambda x: self.distances[self.nodo_actual][x])
                # Actualizamos la demanda
                self.demanda_actual += self.cvrp.demandas[target-1]
                # Actualizamos el nodo actual
                self.nodo_actual = target
                # Agregamos el target a la ruta
                route.append(target)
                # Marcamos el target como visitado
                self.visited[target-1] = 1
            else:
                # Actualizamos el nodo actual al deposito
                self.nodo_actual = 0
                # Actualizamos la demanda
                self.demanda_actual = 0
        
        return route    

class CrossoverOperator:
    """Clase para definir y aplicar operadores de cruce y mutación."""
    
    @staticmethod
    def order_crossover(parent1, parent2):
        """Realiza el crossover de orden (Order Crossover - OX) para dos padres."""
        size = len(parent1)
        point1, point2 = sorted(random.sample(range(size), 2))
        child1 = CrossoverOperator.fill_child(parent1, parent2, point1, point2)
        child2 = CrossoverOperator.fill_child(parent2, parent1, point1, point2)
        return child1, child2
        
    @staticmethod
    def fill_child(parent1, parent2, point1, point2):
        """Llena un hijo con genes de los padres usando el cruce de orden."""
        size = len(parent1)
        child = [None] * size
        child[point1:point2] = parent1[point1:point2]
        fill_pos = point2
        for gene in parent2:
            if gene not in child:
                while child[fill_pos] is not None:
                    fill_pos = (fill_pos + 1) % size
                child[fill_pos] = gene
                fill_pos = (fill_pos + 1) % size
        return child
    
    @staticmethod
    def swap_node_mutation(individual):
        """Realiza una mutación de intercambio de nodos en un individuo."""
        size = len(individual)
        if size < 2:
            return individual
        
        node1, node2 = random.sample(range(size), 2)
        individual[node1], individual[node2] = individual[node2], individual[node1]
        return individual
    
    @staticmethod
    def combined_crossover_and_mutation(parent1, parent2):
        """Decide realizar un crossover clásico o una mutación de intercambio de nodos."""
        if random.random() < 0.75:
            # Realizar crossover de orden
            return CrossoverOperator.order_crossover(parent1, parent2)
        else:
            # Realizar swap node mutation en ambos padres, sin crossover
            mutated_parent1 = CrossoverOperator.swap_node_mutation(parent1.copy())
            mutated_parent2 = CrossoverOperator.swap_node_mutation(parent2.copy())
            return mutated_parent1, mutated_parent2


# In[5]:


class MutationOperator:
    """Clase para definir y aplicar operadores de mutación."""
    
    @staticmethod
    def inversion_mutation(individual):
        """Aplica el operador de inversión de una secuencia dentro del cromosoma
        a un individuo.

        Args:
            individual (list of int): El individuo al que se aplicará el operador.

        Returns:
            list of int: El nuevo individuo con una subcadena invertida.
        """
        ind = individual.copy()
        size = len(ind)
        point1, point2 = sorted(random.sample(range(size), 2))
        ind[point1:point2+1] = ind[point1:point2+1][::-1]
        return ind
        
    @staticmethod
    def swap_sequence_mutation(individual):
        """Intercambia dos subsecuencias disjuntas del individuo."""
        ind = individual.copy()
        size = len(ind)
        if size < 4:
            return ind  # No hay espacio suficiente

        # Seleccionar el primer bloque
        point1 = random.randint(0, size - 4)
        point2 = random.randint(point1 + 1, size - 3)

        # Seleccionar el segundo bloque después del primero
        point3 = random.randint(point2 + 1, size - 2)
        point4 = random.randint(point3 + 1, size - 1)

        # Extraer las subsecuencias
        subseq1 = ind[point1:point2 + 1]
        subseq2 = ind[point3:point4 + 1]

        # Reconstruir el individuo con los bloques intercambiados
        new_individual = (
            ind[:point1] +
            subseq2 +
            ind[point2 + 1:point3] +
            subseq1 +
            ind[point4 + 1:]
        )

        return new_individual


# In[6]:


class GeneticAlgorithm:
    def __init__(self, cvrp, population_size, num_generations, mutation_rate, use_elitism=True, gready = True ,homogenia=True,verbose=False,grafica=False, estrategia_2opt='NO_2OPT', reinicio=False, tipo_mutacion='inversion', poblacion_inicial= None,freq_2opt=10):
        # Configuración del problema
        self.cvrp = cvrp
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate

        # Configuración para quedarse con los mejores individuos
        self.use_elitism = use_elitism

        # Configuración de la población inicial
        self.gready = gready
        self.homogenia = homogenia

        # Flags para el algoritmo
        self.estrategia_2opt = estrategia_2opt
        self.reinicio = reinicio
        self.tipo_mutacion = tipo_mutacion

        self.freq_2opt = freq_2opt  # <--- y aquí lo guardas como atributo

        if poblacion_inicial:
            # En caso de que se pase una poblacion inicial como argumento
            # Ejem: Resultado de algoritmo ACO
            self.population = poblacion_inicial
        elif gready:
            # Si se usa el algoritmo greedy
            # Puede ser homogénea (homogenia = True) o heterogénea (homogenia = False)
            # generamos una población inicial homogénea: todos los individuos son iguales
            # o una población inicial heterogénea: todos los individuos son diferentes con un swap node
            self.population = self.generate_initial_population_gready()
        else:
            # Caso contrario, generamos una población inicial aleatoria
            self.population = self.generate_initial_population(population_size, cvrp.num_clientes)

        
        # Configuración de la clase de fitness
        self.fitness = Fitness(cvrp.matriz_distancias, cvrp.demandas, cvrp.deposito.Q)
        self.optimizer = Optimizer(cvrp.matriz_distancias)


        self.best_fitness = float('-inf')  # Inicializar con un valor alto
        self.verbose = verbose
        self.grafica = grafica
        
    
    
    def generate_initial_population_gready(self):
        individual = GreadyAlgorithm(self.cvrp).get_individual()
        if self.homogenia:
            return [individual] * self.population_size
        else:
            return self.combine([individual] * self.population_size)
    
    def combine(self,population):
        new_population = []
        # Creamos una poblacion heterogenea
        # Cruzaremos con el swap_sequence_mutation
        for ind in population:
            new_individual = CrossoverOperator.swap_node_mutation(ind)
            new_population.append(new_individual)   

        return new_population


    def decode_individual(self,individual, vehicle_capacity, demands):
        """Decodifica un individuo en rutas específicas considerando la capacidad de los vehículos.    
        """
        routes = []
        current_route = []
        current_load = 0
    
        for customer in individual:
            if current_load + demands[customer - 1] <= vehicle_capacity:
                current_route.append(customer)
                current_load += demands[customer - 1]
            else:
                routes.append(current_route)
                current_route = [customer]
                current_load = demands[customer - 1]
    
        if current_route:
            routes.append(current_route)
    
        return routes

    def generate_initial_population(self, n_population, num_customers):
        """Genera una población inicial para un algoritmo genético."""
        population = []
        for _ in range(n_population):
            individual = random.sample(range(1, num_customers + 1), num_customers)
            population.append(individual)
        return population

    def tournament_selection(self, population, fitnesses, selection_probability=0.75):
        """Realiza una selección de torneo binario probabilístico para elegir un individuo de la población."""
        i1, i2 = random.sample(range(len(population)), 2)
        ind1, ind2 = population[i1], population[i2]
        fit1, fit2 = fitnesses[i1], fitnesses[i2]

        if fit1 > fit2:
            return ind1 if random.random() < selection_probability else ind2
        else:
            return ind2 if random.random() < selection_probability else ind1
    
    def filtration(self):
        unique_population = []
        seen = set()
        for individual in self.population:
            tuple_ind = tuple(individual)
            if tuple_ind not in seen:
                unique_population.append(individual)
                seen.add(tuple_ind)
            else:
                unique_population.append(random.sample(range(1, self.cvrp.num_clientes + 1), self.cvrp.num_clientes))
        self.population = unique_population

    def evolve(self):
        self.fitness.fit(self.population)

        if self.verbose:
            # Print initial population
            print(f"\nGeneración 0")
            for ind, fit, cost in zip(self.population, self.fitness.fitness_values, self.fitness.total_costs):
                print(f"Individuo: {ind} - Fitness: {fit:.4f} - Total Cost: {cost:.2f}")
    
            print(f'Mejor Individuo: {self.fitness.best_individuo} - Fitness: {self.fitness.best_fitness_ind:.4f} - Total Cost :{self.fitness.best_total_cost:.2f}')

        for generation in range(self.num_generations):
            new_population = []

            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(self.population, self.fitness.normalized_fitness)
                parent2 = self.tournament_selection(self.population, self.fitness.normalized_fitness)
                child1, child2 = CrossoverOperator.combined_crossover_and_mutation(parent1, parent2)

                # Aplicamos la mutación
                if random.random() < self.mutation_rate:
                    if self.tipo_mutacion == 'inversion':
                        child1 = MutationOperator.inversion_mutation(child1)
                        child2 = MutationOperator.inversion_mutation(child2)
                    elif self.tipo_mutacion == 'swap_sequence':
                        child1 = MutationOperator.swap_sequence_mutation(child1)
                        child2 = MutationOperator.swap_sequence_mutation(child2)

                if self.estrategia_2opt == 'EACH_GEN':
                    rutas1 = self.fitness.decode_individual(child1)
                    rutas2 = self.fitness.decode_individual(child2)
                    rutas1 = self.optimizer.routes_2opt(rutas1)
                    rutas2 = self.optimizer.routes_2opt(rutas2)
                    child1 = [c for r in rutas1 for c in r if c != 0]
                    child2 = [c for r in rutas2 for c in r if c != 0]
                # Optimizamos con un algoritmo 2-opt
                #child1 = self.optimizer.algorithm_2opt(child1)
                new_population.append(child1)


                if len(new_population) < self.population_size:
                    #child2 = self.optimizer.algorithm_2opt(child2)
                    new_population.append(child2)
            
            # Actualizamos la población
            if self.use_elitism:
                combined_population = self.population + new_population
                combined_population.sort(key=lambda ind: self.fitness.fitness_function(ind), reverse=True)
                self.population = combined_population[:self.population_size]
            else:
                self.population = new_population.copy()

            # Aplicamos el operador de filtrado cada 50 generaciones
            if generation % 50 == 49 :
                self.filtration()

            if generation % self.freq_2opt == 0 and self.estrategia_2opt == 'GEN_X':
                self.population = [[c for r in self.optimizer.routes_2opt(self.fitness.decode_individual(ind)) for c in r if c != 0] for ind in self.population]


                    

            # Calculamos la aptitud de la nueva población
            self.fitness.fit(self.population)           

            current_best_fitness = self.fitness.best_fitness_ind
            current_best_individual = self.fitness.best_individuo.copy()
            #current_total_cost = self.fitness.best_total_cost

            if self.estrategia_2opt == 'TOP_GEN':
                # Identificar el mejor de la población
                best_index = self.fitness.normalized_fitness.index(max(self.fitness.normalized_fitness))
                current_best_individual = self.population[best_index]
                
                # Aplicar 2-opt sobre sus rutas decodificadas
                rutas = self.fitness.decode_individual(current_best_individual)
                rutas = self.optimizer.routes_2opt(rutas)
                individuo_optimizado = [c for r in rutas for c in r if c != 0]

                # Recalcular fitness y costo
                current_best_fitness = self.fitness.fitness_function(individuo_optimizado)
                #current_total_cost = self.fitness.calculate_total_cost(rutas)

                # Reemplazar el mejor en la población por su versión optimizada
                self.population[best_index] = individuo_optimizado

            if current_best_fitness > self.best_fitness:
                
                if self.verbose :
                    # Print all individuals, their fitness, and total cost for the current generation
                
                    for ind, fit, cost in zip(self.population, self.fitness.fitness_values, self.fitness.total_costs):
                        print(f"Individuo: {ind} - Fitness: {fit:.4f} - Total Cost: {cost:.2f}")
                    print(f'Mejor Individuo: {self.fitness.best_individuo} - Fitness: {self.fitness.best_fitness_ind:.4f} - Total Cost :{self.fitness.best_total_cost:.2f}')
                self.best_fitness = current_best_fitness
                self.best_individual = current_best_individual.copy()
                decoded_routes = self.decode_individual(self.best_individual, self.cvrp.deposito.Q, self.cvrp.demandas)
                if self.grafica:
                    print(f"\nGeneración {generation + 1}")
                    self.cvrp.graficar(decoded_routes)


        if self.estrategia_2opt == 'FINAL':
            # Aplicamos el operador de 2-opt a la mejor solución de la generación
            rutas = self.fitness.decode_individual(self.best_individual)
            rutas = self.optimizer.routes_2opt(rutas)
            self.best_individual = [c for r in rutas for c in r if c != 0]
            self.best_fitness = self.fitness.fitness_function(self.best_individual)
            self.best_total_cost = self.fitness.calculate_total_cost(rutas)

        return self.fitness.best_individuo , self.fitness.best_total_cost , decoded_routes





