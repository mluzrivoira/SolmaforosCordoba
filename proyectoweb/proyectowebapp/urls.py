from django.urls import path
from . import views
from proyectowebapp.views import home, indiceuv, graficos, importancia

urlpatterns = [
    path('', home, name="home"),
    path('indiceuv', indiceuv, name="indiceuv"),
    path('importancia', importancia, name="importancia"),
    path('graficos', graficos, name="graficos"),
    path('descargar-excel/', views.exportar_excel, name='descargar_excel'),
]
