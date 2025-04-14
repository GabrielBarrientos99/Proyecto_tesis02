from django.db import models

# Create your models here.

class benchmark(models.Model):
    name_model = models.CharField(max_length=100,default='None',unique=True)
    num_customers = models.IntegerField()
    num_vehicles = models.IntegerField()
    capacity = models.IntegerField()
    cost_solution = models.FloatField(null=True, blank=True)  # 👈 Aquí el nuevo campo

class VRPInstance(models.Model):
    name_model = models.ForeignKey(benchmark, on_delete=models.CASCADE)
    population_size = models.IntegerField(null=True, blank=True)
    num_generations = models.IntegerField(null=True, blank=True)
    mutation_rate = models.FloatField(null=True, blank=True)
    use_elitism = models.BooleanField(default=True)

class Table_iterations(models.Model):
    instance = models.ForeignKey(VRPInstance, on_delete=models.CASCADE)
    cost_i1 = models.FloatField(default=0)
    cost_i2 = models.FloatField(default=0)
    cost_i3 = models.FloatField(default=0)
    cost_i4 = models.FloatField(default= 0)
    cost_i5 = models.FloatField(default=0)
    cost_i6 = models.FloatField(default=0)
    best_cost = models.FloatField(default=0)


class Table_benchmark(models.Model):
    instance = models.ForeignKey(VRPInstance, on_delete=models.CASCADE)
    n_nodos = models.IntegerField()
    demand = models.FloatField(default=0)
    best_routes = models.TextField()
    best_individual = models.TextField()
    best_cost = models.FloatField(default=0)
    best_k = models.IntegerField(default=0)
    cost_solution = models.FloatField(default=0)

# Modelos de mis experimentos

class EstrategiaExperimento(models.Model):
    nombre = models.CharField(max_length=100)  # Ej: AG-BASE, ACO-OPT2, HIBRIDO-A2G
    algoritmo = models.CharField(max_length=50, choices=[
        ('AG', 'Algoritmo Genético'),
        ('ACO', 'ACO'),
        ('HIBRIDO', 'Híbrido')
    ])
    descripcion = models.TextField(blank=True)


class ConfiguracionExperimento(models.Model):
    estrategia = models.ForeignKey(EstrategiaExperimento, on_delete=models.CASCADE)
    instancia = models.ForeignKey(VRPInstance, on_delete=models.CASCADE)
    
    # Parámetros AG
    population_size = models.IntegerField(null=True, blank=True)
    num_generations = models.IntegerField(null=True, blank=True)
    mutation_rate = models.FloatField(null=True, blank=True)
    use_elitism = models.BooleanField(null=True, blank=True)
    
    # Parámetros ACO
    num_ants = models.IntegerField(null=True, blank=True)
    max_iter = models.IntegerField(null=True, blank=True)
    alpha = models.FloatField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)
    evaporation_rate = models.FloatField(null=True, blank=True)
    
    # Flags generales
    reinicio = models.BooleanField(default=False)
    hibridacion = models.BooleanField(default=False)
    poblacion_desde_aco = models.BooleanField(default=False)
    tipo_mutacion = models.CharField(
            max_length=20,
            choices=[('inversion', 'Inversión'), ('swap_sequence', 'Intercambio de Secuencias')],
            default='inversion' )
    estrategia_2opt = models.CharField(
            max_length=20,
            choices=[
                # AG
                ('NO_2OPT', 'No aplicar'),
                ('EACH_GEN', 'Cada hijo (AG)'),
                ('GEN_X', 'Cada N generaciones (AG)'),
                ('TOP_GEN', 'Top de la generación (AG)'),
                ('FINAL', 'Solo al final (AG/ACO)'),
                
                # ACO
                ('ALL', 'Todas las hormigas (ACO)'),
                ('STUCK', 'Si se estanca (ACO)'),
                ('LAST', 'Ultima hormiga (ACO)'),
            ],
            default='NO_2OPT'
        )
    
    # Parámetros de optimización para ACO
    usar_swap = models.BooleanField(default=False)
    reinicio_adaptativo = models.BooleanField(default=False)
    restriccion_nodos = models.BooleanField(default=True)
    ajuste_dinamico = models.BooleanField(default=True)
    exportar_poblacion = models.BooleanField(default=False)

    freq_2opt = models.IntegerField(null=True, blank=True, default=10)
    timestamp = models.DateTimeField(auto_now_add=True)

class ResultadoRepeticion(models.Model):
    configuracion = models.ForeignKey(ConfiguracionExperimento, on_delete=models.CASCADE)
    iteracion = models.IntegerField()
    
    costo_obtenido = models.FloatField()
    tiempo_ejecucion = models.FloatField()
    gap_porcentual = models.FloatField(null=True, blank=True)
    costo_optimo = models.FloatField(null=True, blank=True)
    iteracion_mejora = models.IntegerField(null=True, blank=True)
    
     #  Resultado técnico
    mejor_ruta = models.JSONField(blank=True, null=True)  # Lista de rutas: [[1,5,8], [3,7],...]
    
    # Visualización
    path_imagen_solucion = models.CharField(max_length=255, blank=True)  # Ruta al .png generado con Problema_CVRP

class ResumenExperimento(models.Model):
    configuracion = models.OneToOneField(ConfiguracionExperimento, on_delete=models.CASCADE)
    promedio_costo = models.FloatField()
    promedio_gap = models.FloatField()
    tiempo_total = models.FloatField()
    mejor_resultado = models.FloatField()
    desviacion_estandar = models.FloatField()
