from django.db import models


# Create your models here.
class Location(models.Model):
    id = models.FloatField(primary_key=True, verbose_name="ID")
    lat = models.FloatField(verbose_name="Lat", default=32.0)
    lon = models.FloatField(verbose_name="Lon", default=64.0)
    localidad = models.CharField(max_length=100, verbose_name="Localidad")
    ubicacion = models.CharField(max_length=100, verbose_name="Ubicacion")
    
    
    class meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades" 
        ordering = ["localidad"]
    def __str__(self):
        return self.localidad
    
class Medicion(models.Model):
    ubicacion_id = models.IntegerField(default=0) 
    ubicacion = models.CharField(max_length=100, default="Desconocida")
    temperatura = models.FloatField(default=0)
    uv = models.FloatField(default=0)
    latitud = models.FloatField(default=0)
    longitud = models.FloatField(default=0)
    fecha_hora = models.DateTimeField(auto_now_add=True)  # Fecha y hora de recepción del mensaje
    color_uv = models.CharField(max_length=20, default='yellow')  # Nuevo campo para almacenar el color
    


    def __str__(self):
        return f"{self.ubicacion} - {self.fecha_hora}"
