from django.urls import path
from proyectowebapp.views import home, indiceuv, graficos, importancia
from . import views

urlpatterns = [
    path('', home, name="home"), #no tiene url pq es el inicio
    path('indiceuv', indiceuv, name="indiceuv"),
    path('importancia', importancia, name="importancia"),
    path('graficos', graficos, name="graficos"),
    path('descargar-excel/', views.exportar_excel, name='descargar_excel'),
]
