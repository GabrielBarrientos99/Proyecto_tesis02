from django.db import models

# Create your models here.

class benchmark(models.Model):
    name_model = models.CharField(max_length=100,default='None')
    num_customers = models.IntegerField()
    num_vehicles = models.IntegerField()
    capacity = models.IntegerField()

class VRPInstance(models.Model):
    name_model = models.ForeignKey(benchmark, on_delete=models.CASCADE)
    population_size = models.IntegerField()
    num_generations = models.IntegerField()
    mutation_rate = models.FloatField(default=0.01)
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


