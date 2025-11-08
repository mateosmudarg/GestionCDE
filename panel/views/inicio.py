from django.shortcuts import render
from django.db.models import Sum, F, Count, Avg
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
from eventos.models import Evento
from ventas.models import Venta
from ventas.models import Producto
import json
from decimal import Decimal

@login_required
def dashboard_inicio(request):
    # Métricas básicas
    total_eventos = Evento.objects.count()
    total_ventas = Venta.objects.count()
    
    # Cálculo de ganancias
    ventas_totales = Venta.objects.all()
    total_ganancias = sum(venta.total() for venta in ventas_totales)
    ganancias_netas = sum(venta.ganancia() for venta in ventas_totales)
    
    # Convertir Decimal a float para evitar errores de serialización
    total_ganancias = float(total_ganancias) if isinstance(total_ganancias, Decimal) else total_ganancias
    ganancias_netas = float(ganancias_netas) if isinstance(ganancias_netas, Decimal) else ganancias_netas
    
    # Métricas adicionales
    eventos_proximos = Evento.objects.filter(fecha__gte=timezone.now().date()).count()
    
    # Ventas del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ventas_mes = Venta.objects.filter(fecha_hora__gte=inicio_mes).count()
    
    ganancias_mes_query = Venta.objects.filter(fecha_hora__gte=inicio_mes)
    ganancias_mes = sum(venta.total() for venta in ganancias_mes_query)
    ganancias_mes = float(ganancias_mes) if isinstance(ganancias_mes, Decimal) else ganancias_mes
    
    # Cálculo de margen de ganancia
    margen_ganancia = (ganancias_netas / total_ganancias * 100) if total_ganancias > 0 else 0
    
    # Productos más vendidos
    productos_mas_vendidos = Producto.objects.annotate(
        total_vendido=Sum('venta__cantidad')
    ).order_by('-total_vendido')[:5]
    
    labels_productos = [p.nombre for p in productos_mas_vendidos]
    data_productos = [p.total_vendido or 0 for p in productos_mas_vendidos]
    
    # Distribución de medios de pago - SOLO EFECTIVO Y MERCADO PAGO
    ventas_efectivo = Venta.objects.filter(medio_de_pago='Efectivo').aggregate(
        total=Sum('precio_unitario_venta')
    )['total'] or 0
    ventas_mp = Venta.objects.filter(medio_de_pago='Mercado Pago').aggregate(
        total=Sum('precio_unitario_venta')
    )['total'] or 0
    
    # Convertir Decimal a float
    ventas_efectivo = float(ventas_efectivo) if isinstance(ventas_efectivo, Decimal) else ventas_efectivo
    ventas_mp = float(ventas_mp) if isinstance(ventas_mp, Decimal) else ventas_mp
    
    distribucion_pagos = [ventas_efectivo, ventas_mp]
    
    # Top eventos por ventas - DATOS REALES
    eventos_top = Evento.objects.annotate(
        total_ventas=Sum('venta__precio_unitario_venta')
    ).filter(total_ventas__isnull=False).order_by('-total_ventas')[:5]
    
    labels_eventos = [e.nombre for e in eventos_top]
    data_eventos = []
    for e in eventos_top:
        total = e.total_ventas or 0
        # Convertir Decimal a float
        total = float(total) if isinstance(total, Decimal) else total
        data_eventos.append(total)
    
    # Métricas de rendimiento
    ticket_promedio = total_ganancias / total_ventas if total_ventas > 0 else 0
    productos_por_venta_query = Venta.objects.aggregate(avg=Avg('cantidad'))
    productos_por_venta = productos_por_venta_query['avg'] or 0
    productos_por_venta = float(productos_por_venta) if isinstance(productos_por_venta, Decimal) else productos_por_venta
    
    eficiencia_ventas = min(100, (ventas_mes / max(1, total_ventas) * 100 * 4))  # Ejemplo simplificado
    
    # Ventas recientes
    ventas_recientes = Venta.objects.select_related('producto').order_by('-fecha_hora')[:5]
    
    context = {
        'total_eventos': total_eventos,
        'total_ventas': total_ventas,
        'total_ganancias': total_ganancias,
        'ganancias_netas': ganancias_netas,
        'eventos_proximos': eventos_proximos,
        'ventas_mes': ventas_mes,
        'ganancias_mes': ganancias_mes,
        'margen_ganancia': round(margen_ganancia, 1),
        'labels_productos': json.dumps(labels_productos),
        'data_productos': json.dumps(data_productos),
        'distribucion_pagos': json.dumps(distribucion_pagos),
        'labels_eventos': json.dumps(labels_eventos),
        'data_eventos': json.dumps(data_eventos),
        'ticket_promedio': round(ticket_promedio, 2),
        'productos_por_venta': round(productos_por_venta, 1),
        'eficiencia_ventas': round(eficiencia_ventas, 1),
        'ventas_recientes': ventas_recientes,
        'fecha_actual': timezone.now(),
    }
    
    return render(request, 'inicio.html', context)
