from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(benchmark)
admin.site.register(VRPInstance)
admin.site.register(Table_iterations)
admin.site.register(Table_benchmark)
