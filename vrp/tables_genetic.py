import os
from .Problema_CVRP import CVRP
from .Lectura_Instancia import VRPFileReader
from .Algoritmo_Genetico_CVRP import GeneticAlgorithm,Fitness
from .models import benchmark, VRPInstance, Table_iterations, Table_benchmark

class GeneticAlgorithmTable():
    def __init__(self,lista_modelos):
        '''
        Constructor de la clase GeneticAlgorithmTable
        Inicializa la clase con la lista de modelos a ejecutar

        Parameters
        ----------
        lista_modelos : list
            Lista de modelos (cvrp , ga_params) a ejecutar

            ga_params : dict
                Diccionario con los parametros del algoritmo genetico
                population_size : int
                    Tamaño de la población
                num_generations : int
                    Número de generaciones
                mutation_rate : float
                    Tasa de mutación
                use_elitism : bool  
                    Booleano que indica si se usa elitismo               

        '''
        self.lista_modelos = lista_modelos

    def add_data(self,d1,d2,d3,d4):
        # Crear y guardar una instancia de benchmark
        benchmark_instance = benchmark.objects.create(
            name_model=d1['name_model'],
            num_customers=d1['num_customers'],
            num_vehicles=d1['num_vehicles'],
            capacity=d1['capacity']
        )

        # Crear y guardar una instancia de VRPInstance
        vrp_instance = VRPInstance.objects.create(
            name_model=benchmark_instance,
            population_size=d2['population_size'],
            num_generations=d2['num_generations'],
            mutation_rate=d2['mutation_rate'],
            use_elitism=d2['use_elitism']
        )

        # Crear y guardar una instancia de Table_iterations
        table_iterations_instance = Table_iterations.objects.create(
            instance=vrp_instance,
            cost_i1=round(d3['cost_i'][0][1], 2),  # Aproximar a 2 decimales
            cost_i2=round(d3['cost_i'][1][1], 2),  # Aproximar a 2 decimales
            cost_i3=round(d3['cost_i'][2][1], 2),  # Aproximar a 2 decimales
            cost_i4=round(d3['cost_i'][3][1], 2),  # Aproximar a 2 decimales
            cost_i5=round(d3['cost_i'][4][1], 2),  # Aproximar a 2 decimales
            cost_i6=round(d3['cost_i'][5][1], 2),  # Aproximar a 2 decimales
            best_cost=round(d3['best_cost'], 2)    # Aproximar a 2 decimales
        )
        # Formatear las mejores rutas como un string
        rutas = ''
        for i in range(len(d4['best_routes'])):
            rutas += f'Ruta {i+1}: {d4["best_routes"][i]}\n'
            

        # Crear y guardar una instancia de Table_benchmark
        table_benchmark_instance = Table_benchmark.objects.create(
            instance=vrp_instance,
            n_nodos=d4['n_nodos'],
            demand=round(d4['demand'], 2),  # Aproximar a 2 decimales
            best_routes=rutas,
            best_individual=d4['best_individual'],
            best_cost=round(d4['best_cost'], 2),  # Aproximar a 2 decimales
            best_k=len(d4['best_routes']),
            cost_solution=round(d4['cost_solution'], 2)  # Aproximar a 2 decimales
        )


    
    def execute(self):
        '''
        Método que ejecuta los modelos de la lista de modelos

        Se ejecuta el algoritmo genetico para el modelo 6 veces y se almacena el costo de cada iteración
        en la tabla Table_iterations y el mejor costo en la tabla benchmark
        '''
        for modelo in self.lista_modelos:
            cvrp = modelo[0]
            ga_params = modelo[1]

            # Almacenamos los parametros del AG
            population_size = ga_params['population_size']
            num_generations = ga_params['num_generations']
            mutation_rate = ga_params['mutation_rate']
            use_elitism = ga_params['use_elitism']


            # Almacenamos datos
            model_name = cvrp.model_name
            n_nodos = cvrp.num_clientes
            costos_i = []

            
            
            # Correr el algoritmo 6 iteraciones
            for i in range(6):
                #self, cvrp, population_size, num_generations, mutation_rate, use_elitism=True, gready = True ,homogenia=True,verbose=False,grafica=False
                ga = GeneticAlgorithm(cvrp, population_size, num_generations, mutation_rate, use_elitism)
                best_individuo ,best_total_cost , decoded_routes = ga.evolve()
                costos_i.append( (best_individuo ,best_total_cost , decoded_routes) )

            # Encontrar la tupla solucion con menor costo
            best_cost = min(costos_i, key = lambda x: x[1])

            # Recogemos la solucion 
            cost_solution = self.extraer_solution(model_name=model_name,cvrp= cvrp)

            # Creamos nuestro diccionario de datos
            benchmark_instance = {
                'name_model': model_name,
                'num_customers': n_nodos,
                'num_vehicles': cvrp.deposito.k,
                'capacity': cvrp.deposito.Q
            }

            vrp_instance = {
                'name_model': model_name,
                'population_size': population_size,
                'num_generations': num_generations,
                'mutation_rate': mutation_rate,
                'use_elitism': use_elitism
            }

            table_iterations = {
                'instance': vrp_instance,
                'cost_i' : costos_i,
                'best_cost': best_cost[1]
            }

            table_benchmark = {
                'instance': vrp_instance,
                'n_nodos': n_nodos,
                'demand': sum(cvrp.demandas),
                'best_routes': best_cost[2],
                'best_individual': best_cost[0],
                'best_cost': best_cost[1],
                'best_k': cvrp.deposito.k,
                'cost_solution': cost_solution
            }

            # Guardamos los datos
            self.add_data(benchmark_instance,vrp_instance,table_iterations,table_benchmark)

    def get_data(self):
        '''
        Método que retorna los datos de las tablas benchmark, Table_iterations y Table_benchmark
        '''
        data = {
            'benchmark': benchmark.objects.all(),
            'VRPInstance': VRPInstance.objects.all(),
            'Table_iterations': Table_iterations.objects.all(),
            'Table_benchmark': Table_benchmark.objects.all()
        }

        return data
    
    def extraer_solution(self,model_name,cvrp):
        '''
        Método que completa la tabla Table_benchmark con el costo de la solución
        '''        
        
        pre_dir=''
        if 'Golden' in model_name:
            pre_dir='Golden'
        elif 'M' in model_name:
            pre_dir='M-Cristofides'
        else:
            pre_dir=model_name.split('-')[0]


        file_path = os.path.join('vrp', 'static', 'instancias', pre_dir, f'{model_name}.vrp')
        file_path_solution = file_path.replace('.vrp', '.sol')   


        rutas,cost = VRPFileReader.read_sol_file(file_path_solution)
        cost_solution = cvrp.calcular_costo_total(rutas)   #Solo usamos la función para calcular el costo total    

        return cost_solution 
            

    