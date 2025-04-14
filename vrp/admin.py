from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(benchmark)
admin.site.register(VRPInstance)
admin.site.register(Table_iterations)
admin.site.register(Table_benchmark)

# Nuevos modelos para experimentos comparativos
admin.site.register(EstrategiaExperimento)
admin.site.register(ConfiguracionExperimento)
admin.site.register(ResultadoRepeticion)
admin.site.register(ResumenExperimento)