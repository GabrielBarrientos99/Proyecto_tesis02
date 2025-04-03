from django.conf import settings
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
import os
from .Problema_CVRP import CVRP
from .Lectura_Instancia import VRPFileReader
from .Algoritmo_Genetico_CVRP import GeneticAlgorithm
from .models import benchmark, VRPInstance, Table_iterations, Table_benchmark
from .tables_genetic import GeneticAlgorithmTable
from django.views.decorators.csrf import csrf_exempt
import json
from .Pruebas_generator import Image_Controler
from django.http import JsonResponse
import matplotlib
from .ACO import AntColonyOptimizer_v2
matplotlib.use('Agg')


def listar_instancias():
    instancias_dir = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias')
    instancias = {}
    for root, dirs, files in os.walk(instancias_dir):
        if root == instancias_dir:
            continue
        categoria = os.path.basename(root)
        instancias[categoria] = [os.path.join(categoria, f) for f in files if f.endswith('.vrp')]
        # Creamos un acceso a la solucion para cada instancia
        solucion = categoria + '-sol'
        instancias[solucion] = [os.path.join(categoria, f) for f in files if f.endswith('.sol')]
    return instancias

def generar_grafico(request):
    if request.method == 'GET' and 'instancia' in request.GET:
        instancia = request.GET['instancia']
        mostrar_solucion = request.GET.get('mostrar_solucion')
        file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', instancia)
        output_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', 'grafico.png')
        if os.path.exists(file_path):
            cvrp = CVRP(file_path=file_path, file_save=output_path)
            cvrp.graficar()

            solution_file_path = None
            if mostrar_solucion == 'si':
                solution_file_path = file_path.replace('.vrp', '.sol')
                routes_solution, cost_solution = VRPFileReader.read_sol_file(solution_file_path)
                solution_graph_file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', 'grafico_solucion.png')
                cvrp.file_save = solution_graph_file_path
                cvrp.graficar(routes_solution)
            else:
                solution_graph_file_path = None

            instance_info = {
                'num_clientes': cvrp.num_clientes,
                'capacidad': cvrp.deposito.Q,
                'num_vehiculos': 'No Disponible',
            }
            return render(request, 'inicio.html', {
                'file_path': 'instancias/grafico.png',
                'solution_file_path': 'instancias/grafico_solucion.png' if solution_graph_file_path else None,
                'instancias': listar_instancias(),
                'instance_info': instance_info,
                'selected_instance': instancia
            })
        else:
            return HttpResponse("Archivo no encontrado", status=404)
    else:
        return render(request, 'inicio.html', {'instancias': listar_instancias()})

def inicio(request):
    return render(request, 'inicio.html', {'instancias': listar_instancias()})

def aco(request):
    if request.method == 'POST':
        # Capturamos los datos del formulario
        instancia = request.POST['instancia']
        num_ants = int(request.POST['num_ants'])
        max_iter = int(request.POST['max_iter'])
        alpha = float(request.POST['alpha'])
        beta = float(request.POST['beta'])
        evaporation_rate = float(request.POST['evaporation_rate'])
        mostrar_proceso = 'mostrar_proceso' in request.POST

        # Rutas de archivos
        file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', instancia)
        output_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'grafico_aco.png')
        
        if os.path.exists(file_path):
            # Inicializamos el problema CVRP y el optimizador ACO
            cvrp = CVRP(file_path=file_path, file_save=output_path)
            aco = AntColonyOptimizer_v2(
                cvrp=cvrp,
                num_ants=num_ants,
                max_iter=max_iter,
                alpha=alpha,
                beta=beta,
                evaporation_rate=evaporation_rate,
                verbose=mostrar_proceso
            )

            # Ejecutamos el algoritmo ACO
            best_solution, best_cost = aco.train()
            
            # Generamos el gráfico de la mejor solución
            cvrp.graficar(best_solution)

            # Contexto para la plantilla
            context = {
                'file_path': 'grafico_aco.png',
                'instancias': listar_instancias(),
                'selected_instance': instancia,
                'best_solution': best_solution,
                'best_cost': best_cost,
                'num_ants': num_ants,
                'max_iter': max_iter,
                'alpha': alpha,
                'beta': beta,
                'evaporation_rate': evaporation_rate,
                'mostrar_proceso': mostrar_proceso,
            }

            return render(request, 'aco.html', context)
        else:
            return HttpResponse("Archivo no encontrado", status=404)
    else:
        # Contexto para la carga inicial de la página
        context = {
            'instancias': listar_instancias()
        }
        return render(request, 'aco.html', context)

def algoritmo_genetico(request):
    if request.method == 'POST':
        instancia = request.POST['instancia']
        population_size = int(request.POST['population_size'])
        num_generations = int(request.POST['num_generations'])
        mutation_rate = float(request.POST['mutation_rate'])
        use_elitism = 'use_elitism' in request.POST
        mostrar_proceso = 'mostrar_proceso' in request.POST

        file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', instancia)
        output_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'grafico_genetico.png')
        
        if os.path.exists(file_path):
            cvrp = CVRP(file_path=file_path ,  file_save=output_path )
            ga = GeneticAlgorithm(cvrp, population_size, num_generations, mutation_rate, use_elitism, grafica=mostrar_proceso)
            best_individual, best_cost, routes = ga.evolve()

            cvrp.graficar(routes)

            context = {
                'file_path': 'grafico_genetico.png',
                'instancias': listar_instancias(),
                'selected_instance': instancia,
                'best_individual': best_individual,
                'best_cost': best_cost,
                'routes': routes,
                'population_size': population_size,
                'num_generations': num_generations,
                'mutation_rate': mutation_rate,
                'use_elitism': use_elitism,
                'mostrar_proceso': mostrar_proceso,
            }

            return render(request, 'algoritmo_genetico.html', context)
        else:
            return HttpResponse("Archivo no encontrado", status=404)
    else:
        context = {
            'instancias': listar_instancias()
        }
        return render(request, 'algoritmo_genetico.html', context)
    
def run_automation(request):
    context = {
        'instancias': listar_instancias()
    }
    if request.method == 'POST':
        instancias = request.POST.getlist('instancia')
        population_sizes = request.POST.getlist('population_size')
        num_generations_list = request.POST.getlist('num_generations')
        mutation_rates = request.POST.getlist('mutation_rate')
        use_elitism_list = request.POST.getlist('use_elitism')
        #print(instancias, population_sizes, num_generations_list, mutation_rates, use_elitism_list)
        lista_modelos = []
        # Armamos las tuplas (vrp_instance, ga_params)
        for instancia, population_size, num_generations, mutation_rate, use_elitism in zip(instancias, population_sizes, num_generations_list, mutation_rates, use_elitism_list):
            file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', instancia)
            if os.path.exists(file_path):
                cvrp = CVRP(file_path=file_path)
                ga_params = {
                    'population_size': int(population_size),
                    'num_generations': int(num_generations),
                    'mutation_rate': float(mutation_rate),
                    'use_elitism': use_elitism == 'true'
                }
                lista_modelos.append((cvrp, ga_params))
        
        
        
        if lista_modelos:
            ag_executor = GeneticAlgorithmTable(lista_modelos)
            ag_executor.execute()

        # Actualizamos el contexto con la información de las tablas
        context['vrp_instances'] = VRPInstance.objects.all()
        context['table_iterations'] = Table_iterations.objects.all()
        context['table_benchmarks'] = Table_benchmark.objects.all()

        return render(request, 'run_automation.html', context)
    
    context['vrp_instances'] = VRPInstance.objects.all()
    context['table_iterations'] = Table_iterations.objects.all()
    context['table_benchmarks'] = Table_benchmark.objects.all()
    return render(request, 'run_automation.html', context)

def show_details(request, vrp_instance_id):
    vrp_instance = get_object_or_404(VRPInstance, pk=vrp_instance_id)
    iterations = Table_iterations.objects.filter(instance=vrp_instance)
    benchmarks = Table_benchmark.objects.filter(instance=vrp_instance)

    return render(request, 'show_details.html', {
        'vrp_instance': vrp_instance,
        'iterations': iterations,
        'benchmarks': benchmarks
    })

def seleccionar_instancias(request):
    instancias = listar_instancias()
    ic = Image_Controler()
    parametros = ic.params_ag

    return render(request, 'seleccionar_instancias.html', {
        'instancias': instancias,
        'parametros': parametros
    })

def obtener_atributos_instancia(request):
    instancia = request.GET.get('instancia')
    file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', instancia)
    output_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', 'grafico.png')
    output_path_sol = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', 'grafico_solucion.png')

    file_path_sol = file_path.replace('.vrp', '.sol')
    sol, cost = None, None
    if os.path.exists(file_path_sol):
        sol, cost = VRPFileReader.read_sol_file(file_path_sol)

    if os.path.exists(file_path):
        cvrp = CVRP(file_path=file_path, file_save=output_path)
        cvrp.graficar()

        if sol:
            cvrp.file_save = output_path_sol
            cvrp.graficar(sol)

        instance_info = {
            'model_name': cvrp.model_name,
            'num_clientes': cvrp.num_clientes,
            'deposito': {
                'capacity': cvrp.deposito.Q,
            },
            'imagen_instancia': f'/static/instancias/grafico.png',
            'imagen_solucion': f'/static/instancias/grafico_solucion.png' if sol else None,
        }

        return render(request, 'seleccionar_instancias.html', {
            'instancias': listar_instancias(),
            'instance_info': instance_info,
            'selected_instance': instancia,
            'parametros': Image_Controler().params_ag
        })
    else:
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)

@csrf_exempt
def generate_images(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        instancias = data.get('instancias', [])
        ic = Image_Controler()
        json_data = ic.generate_image_json(instancias)
        return JsonResponse(json_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def ejecutar_automatizacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lista_modelos = []
            
            for instancia, detalles in data.items():
                name = instancia  # La clave del diccionario es el nombre de la instancia
                params_ag = detalles['params_ag']  # Los parámetros AG se encuentran en el valor asociado a la clave
                for param in params_ag:
                    file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', name)
                    if os.path.exists(file_path):
                        cvrp = CVRP(file_path=file_path)
                        ga_params = {
                            'population_size': param['population_size'],
                            'num_generations': param['num_generations'],
                            'mutation_rate': param['mutation_rate'],
                            'use_elitism': param['use_elitism']
                        }
                        lista_modelos.append((cvrp, ga_params))
            
            if lista_modelos:
                ag_executor = GeneticAlgorithmTable(lista_modelos)
                ag_executor.execute()
                return JsonResponse({'status': 'Automatización completada'})
            else:
                print("No se encontraron modelos para ejecutar.")
                return JsonResponse({'error': 'No se encontraron modelos para ejecutar.'}, status=400)
        except Exception as e:
            print(f"Error en la automatización: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def parse_routes(routes_string):
    routes = []
    for line in routes_string.split('\n'):
        if line.startswith("Ruta"):
            route = line.split(':')[1].strip()
            route_list = [int(node.strip()) for node in route.strip('[]').split(',')]
            routes.append(route_list)
    return routes

def get_solution_details(request, iteration_id):
    # Obtener la iteración específica
    iteration = get_object_or_404(Table_iterations, id=iteration_id)
    
    # Obtener la instancia relacionada de VRPInstance
    vrp_instance = iteration.instance

    # Obtener los parámetros de la instancia
    parameters = {
        'population_size': vrp_instance.population_size,
        'num_generations': vrp_instance.num_generations,
        'mutation_rate': vrp_instance.mutation_rate,
        'use_elitism': vrp_instance.use_elitism,
    }

    # Obtener la mejor solución desde Table_benchmark
    benchmark = get_object_or_404(Table_benchmark, instance=vrp_instance)

    # Convertir la cadena de rutas en una lista de rutas
    best_routes = parse_routes(benchmark.best_routes)
    solucion_real = benchmark.cost_solution

    # Generar y guardar los gráficos
    model_name = vrp_instance.name_model.name_model
    pre_dir = 'Golden' if 'Golden' in model_name else 'M-Cristofides' if 'M' in model_name else model_name.split('-')[0]
    
    solution_file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', pre_dir, model_name + '.sol')
    best_solution_file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', 'best_solution.png')
    obtained_solution_file_path = os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', 'obtained_solution.png')

    if os.path.exists(solution_file_path):
        routes_solution, cost_solution = VRPFileReader.read_sol_file(solution_file_path)
        
        cvrp = CVRP(file_path=os.path.join(settings.BASE_DIR, 'vrp', 'static', 'instancias', pre_dir, model_name + '.vrp'))
        cvrp.file_save = best_solution_file_path
        cvrp.graficar(best_routes)

        cvrp.file_save = obtained_solution_file_path
        cvrp.graficar(routes_solution)
        
        data = {
            'model_name': model_name,
            'cost_i1': iteration.cost_i1,
            'cost_i2': iteration.cost_i2,
            'cost_i3': iteration.cost_i3,
            'cost_i4': iteration.cost_i4,
            'cost_i5': iteration.cost_i5,
            'cost_i6': iteration.cost_i6,
            'best_cost': iteration.best_cost,
            'parameters': parameters,
            'solucion_real': solucion_real,
            'best_solution_graph_path': 'instancias/best_solution.png' if os.path.exists(best_solution_file_path) else None,
            'obtained_solution_graph_path': 'instancias/obtained_solution.png' if os.path.exists(obtained_solution_file_path) else None,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Solution file not found'}, status=404)