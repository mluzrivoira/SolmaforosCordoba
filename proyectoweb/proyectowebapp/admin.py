from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin
from .models import Location, Medicion

# Crear un recurso para el modelo Medicion
class MedicionResource(resources.ModelResource):
    class Meta:
       model = Medicion

@admin.register(Medicion)
class MedicionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('ubicacion', 'temperatura', 'uv',  'fecha_hora')
    list_filter = ('ubicacion', 'temperatura', 'uv')
    search_fields = ('ubicacion',)
    resource_class = MedicionResource  # Conectar el recurso con el modelo

admin.site.register(Location)