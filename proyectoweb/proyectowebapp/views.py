from django.shortcuts import render, HttpResponse
from .models import Location, Medicion #agregue esto
import folium
from django.http import JsonResponse, HttpResponse
import json
from folium.plugins import BeautifyIcon 
from collections import defaultdict
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Max, Q
import pandas as pd
import pytz
from datetime import datetime, timedelta
from datetime import date, time
arg_tz = pytz.timezone("America/Argentina/Buenos_Aires")

def home(request): 

    return render(request, "proyectowebapp/home.html")

def indiceuv(request):
    # Traer TODAS las mediciones, ordenadas de la más nueva a la más vieja
    # Obtener la última fecha de medición para cada ubicación
    ultimas_fechas = Medicion.objects.values('ubicacion_id').annotate(ultima_fecha=Max('fecha_hora'))

# Luego traemos las mediciones correspondientes a esas fechas

    filtros = Q()
    for dato in ultimas_fechas:
        filtros |= Q(ubicacion_id=dato['ubicacion_id'], fecha_hora=dato['ultima_fecha'])

    mediciones = Medicion.objects.filter(filtros)


    # Creamos el mapa
    initialmap = folium.Map(location=[-32.03855, -63.70726], zoom_start=6)


    # Colores según OMS
    colores_uv = {
        "Verde": "#00cc00",
        "Amarillo": "#ffcc00",
        "Naranja": "#ff9900",
        "Rojo": "#ff3300",
        "Violeta": "#9900cc"
    }


    for medicion in mediciones:
        coordinates = [medicion.latitud, medicion.longitud]


        popup_text = (
            f"ID {medicion.ubicacion_id}<br>"
            f"<strong>{medicion.ubicacion}</strong><br>"
            f"<strong>Temperatura:</strong> {medicion.temperatura} °C<br>"
            f"<strong>UV:</strong> {medicion.uv}<br>"
            f"<strong>Fecha y hora:</strong>{medicion.fecha_hora.astimezone(arg_tz).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Obtener color real desde el diccionario
        color_uv_hex = colores_uv.get(medicion.color_uv, "gray")


        # Crear ícono bonito con BeautifyIcon
        icono = BeautifyIcon(
            icon_shape='marker',
            number=str(int(medicion.uv)),  # Muestra el valor UV dentro del ícono
            border_color=color_uv_hex,
            background_color=color_uv_hex,
            text_color='white'
        )


        # Agregar marcador al mapa
        folium.Marker(
            location=coordinates,
            popup=popup_text,
            icon=icono
        ).add_to(initialmap)


    context = {
        'mapa': initialmap._repr_html_(),
        'locations': mediciones
    }


    return render(request, 'proyectowebapp/indiceuv.html', context)


def importancia(request):
    
    return render(request, "proyectowebapp/importancia.html")


def graficos(request):
    desde_str = request.GET.get("desde")  # e.g. "2025-08-01"
    hasta_str = request.GET.get("hasta")  # e.g. "2025-08-01"


    mediciones_qs = Medicion.objects.all()
    errores = []


    if desde_str and hasta_str:
        try:
            fecha_desde_date = date.fromisoformat(desde_str)
            fecha_hasta_date = date.fromisoformat(hasta_str)


            if fecha_hasta_date < fecha_desde_date:
                errores.append("La fecha 'Hasta' no puede ser anterior a 'Desde'.")
            elif (fecha_hasta_date - fecha_desde_date).days > 7:
                errores.append("El rango máximo permitido es de 7 días.")
            else:
            # Construir los bounds en hora local: desde 00:00 hasta 23:59:59.999999
                inicio_local = datetime.combine(fecha_desde_date, time.min)
                fin_local = datetime.combine(fecha_hasta_date, time.max)
                inicio_local = arg_tz.localize(inicio_local)
                fin_local = arg_tz.localize(fin_local)


                fecha_desde_utc = inicio_local.astimezone(pytz.UTC)
                fecha_hasta_utc = fin_local.astimezone(pytz.UTC)


                mediciones_qs = mediciones_qs.filter(
                    fecha_hora__range=(fecha_desde_utc, fecha_hasta_utc)
                ).order_by("fecha_hora")
        except ValueError:
            errores.append("Formato de fecha inválido. Usar YYYY-MM-DD.")
    else:
        # Si no hay filtro, tomar solo las de "hoy" en hora de Argentina
        ahora_local = datetime.now(tz=arg_tz)
        inicio_local = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_local = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)


        inicio_utc = inicio_local.astimezone(pytz.UTC)
        fin_utc = fin_local.astimezone(pytz.UTC)


        mediciones_qs = mediciones_qs.filter(
            fecha_hora__range=(inicio_utc, fin_utc)
        ).order_by("fecha_hora")


    # Si hay errores, forzamos a que no haya datos para que no se dibujen gráficos
    if errores:
        mediciones_qs = Medicion.objects.none()


    # Eliminar duplicados
    datos_unicos = []
    ya_vistos = set()
    for m in mediciones_qs:
        clave = (
            m.ubicacion_id,
            m.uv,
            m.temperatura,
            m.fecha_hora.strftime("%Y-%m-%d %H:%M"),
        )
        if clave not in ya_vistos:
            ya_vistos.add(clave)
            fecha_iso = m.fecha_hora.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            datos_unicos.append(
                {
                    "ubicacion_id": m.ubicacion_id,
                    "fecha_hora": fecha_iso,
                    "ubicacion": m.ubicacion,
                    "latitud": m.latitud,
                    "longitud": m.longitud,
                    "temperatura": m.temperatura,
                    "uv": m.uv,
                    "color_uv": m.color_uv,
                }
            )


    datos_json = json.dumps(datos_unicos)


    context = {
        "mediciones": datos_unicos,
        "datos_json": datos_json,
        "errores": errores,
        "filtro_desde": desde_str or "",
        "filtro_hasta": hasta_str or "",
    }
    return render(request, "proyectowebapp/graficos.html", context)

def exportar_excel(request):
    mediciones = Medicion.objects.all().order_by('-fecha_hora')

    # Filtrar duplicados por minuto, ubicación, uv y temperatura
    vistos = set()
    datos_filtrados = []

    for m in mediciones:
        clave = (m.ubicacion_id, m.uv, m.temperatura, m.fecha_hora.strftime("%Y-%m-%d %H:%M"))
        if clave not in vistos:
            vistos.add(clave)
            datos_filtrados.append({
                'ubicacion_id': m.ubicacion_id,
                'ubicacion': m.ubicacion,
                'temperatura': m.temperatura,
                'uv': m.uv,
                'fecha_hora': m.fecha_hora.astimezone(arg_tz).replace(tzinfo=None)
            })

    df = pd.DataFrame(datos_filtrados)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=medicionesSOLMAFOROSCBA.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return response

def sobre_nosotros(request):
    return render(request, "proyectowebapp/sobre_nosotros.html")