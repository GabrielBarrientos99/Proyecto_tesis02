from django.urls import path
from vrp import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('generar_grafico/', views.generar_grafico, name='generar_grafico'),
    path('algoritmo_genetico/', views.algoritmo_genetico, name='algoritmo_genetico'),
    path('aco/', views.aco, name='aco'),
    path('run-automation/', views.run_automation, name='run_automation'),
    path('details/<int:vrp_instance_id>/', views.show_details, name='show_details'),
    path('seleccionar_instancias/', views.seleccionar_instancias, name='seleccionar_instancias'),
    path('generate_images/', views.generate_images, name='generate_images'),
    path('obtener_atributos_instancia/', views.obtener_atributos_instancia, name='obtener_atributos_instancia'),
    path('ejecutar_automatizacion/', views.ejecutar_automatizacion, name='ejecutar_automatizacion'),
    path('get-solution-details/<int:iteration_id>/', views.get_solution_details, name='get_solution_details'),

]
