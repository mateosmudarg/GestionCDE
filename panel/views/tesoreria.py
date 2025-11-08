from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from tesoreria.models import Movimiento
from eventos.models import Evento
from decimal import Decimal

@login_required
def ingresos_tesoreria(request):
    """Listado de ingresos con métricas avanzadas"""
    ingresos = Movimiento.objects.filter(tipo='Ingreso').select_related('evento').order_by('-fecha')
    total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0
    
    # Convertir Decimal a float si es necesario
    if isinstance(total_ingresos, Decimal):
        total_ingresos = float(total_ingresos)
    
    # Contar eventos con ingresos
    eventos_count = ingresos.values('evento').distinct().count()
    
    # Obtener lista de eventos para el filtro
    eventos_list = Evento.objects.filter(movimiento__tipo='Ingreso').distinct()
    
    # Ingresos por evento para el gráfico
    eventos_ingresos = Evento.objects.filter(
        movimiento__tipo='Ingreso'
    ).annotate(
        total=Sum('movimiento__monto')
    ).filter(total__isnull=False).order_by('-total')[:6]  # Top 6 eventos
    
    # Convertir Decimal a float para el gráfico
    for evento in eventos_ingresos:
        if isinstance(evento.total, Decimal):
            evento.total = float(evento.total)
    
    context = {
        'movimientos': ingresos,
        'total': total_ingresos,
        'eventos_count': eventos_count,
        'eventos_list': eventos_list,
        'eventos_ingresos': eventos_ingresos,
    }
    
    return render(request, 'tesoreria/ingresos.html', context)

@login_required
def egresos_tesoreria(request):
    """Listado de egresos"""
    egresos = Movimiento.objects.filter(tipo='Egreso').select_related('evento')
    total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0
    
    # Convertir Decimal a float si es necesario
    if isinstance(total_egresos, Decimal):
        total_egresos = float(total_egresos)
    
    return render(request, 'tesoreria/egresos.html', {
        'movimientos': egresos,
        'total': total_egresos
    })

@login_required
def balance_tesoreria(request):
    """Balance: ingresos - egresos con métricas avanzadas"""
    # Totales básicos
    total_ingresos = Movimiento.objects.filter(tipo='Ingreso').aggregate(total=Sum('monto'))['total'] or 0
    total_egresos = Movimiento.objects.filter(tipo='Egreso').aggregate(total=Sum('monto'))['total'] or 0
    balance_total = total_ingresos - total_egresos
    
    # Convertir Decimal a float si es necesario
    if isinstance(total_ingresos, Decimal):
        total_ingresos = float(total_ingresos)
    if isinstance(total_egresos, Decimal):
        total_egresos = float(total_egresos)
    if isinstance(balance_total, Decimal):
        balance_total = float(balance_total)
    
    # Contar transacciones
    ingresos_count = Movimiento.objects.filter(tipo='Ingreso').count()
    egresos_count = Movimiento.objects.filter(tipo='Egreso').count()
    
    # Todos los movimientos
    movimientos = Movimiento.objects.select_related('evento').order_by('-fecha')
    
    # Balance por eventos
    eventos_con_movimientos = Evento.objects.filter(
        movimiento__isnull=False
    ).distinct().annotate(
        total_ingresos=Sum('movimiento__monto', filter=Q(movimiento__tipo='Ingreso')),
        total_egresos=Sum('movimiento__monto', filter=Q(movimiento__tipo='Egreso'))
    )
    
    eventos_con_balance = []
    for evento in eventos_con_movimientos:
        ingresos_evento = evento.total_ingresos or 0
        egresos_evento = evento.total_egresos or 0
        balance_evento = ingresos_evento - egresos_evento
        
        # Convertir Decimal a float
        if isinstance(ingresos_evento, Decimal):
            ingresos_evento = float(ingresos_evento)
        if isinstance(egresos_evento, Decimal):
            egresos_evento = float(egresos_evento)
        if isinstance(balance_evento, Decimal):
            balance_evento = float(balance_evento)
            
        eventos_con_balance.append({
            'nombre': evento.nombre,
            'ingresos': ingresos_evento,
            'egresos': egresos_evento,
            'balance': balance_evento
        })
    
    context = {
        'movimientos': movimientos,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance_total': balance_total,
        'ingresos_count': ingresos_count,
        'egresos_count': egresos_count,
        'eventos_con_balance': eventos_con_balance,
    }
    
    return render(request, 'tesoreria/balance.html', context)