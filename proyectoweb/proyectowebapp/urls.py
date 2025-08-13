from django.urls import path
from . import views
from proyectowebapp.views import home, indiceuv, graficos, importancia, sobre_nosotros, exportar_excel

urlpatterns = [
    path('', home, name="home"),
    path('indiceuv', indiceuv, name="indiceuv"),
    path('importancia', importancia, name="importancia"),
    path('graficos', graficos, name="graficos"),
    path('descargar-excel/', exportar_excel, name='descargar_excel'),
    path('sobre-nosotros', sobre_nosotros, name="sobre_nosotros"),
]
