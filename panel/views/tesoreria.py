from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from tesoreria.models import Movimiento

@login_required
def ingresos(request):
    """Listado de ingresos"""
    ingresos = Movimiento.objects.filter(tipo='Ingreso').select_related('evento')
    total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0
    return render(request, 'tesoreria/ingresos.html', {
        'movimientos': ingresos,
        'total': total_ingresos
    })

@login_required
def egresos(request):
    """Listado de egresos"""
    egresos = Movimiento.objects.filter(tipo='Egreso').select_related('evento')
    total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0
    return render(request, 'tesoreria/egresos.html', {
        'movimientos': egresos,
        'total': total_egresos
    })

@login_required
def balance(request):
    """Balance: ingresos - egresos"""
    total_ingresos = Movimiento.objects.filter(tipo='Ingreso').aggregate(total=Sum('monto'))['total'] or 0
    total_egresos = Movimiento.objects.filter(tipo='Egreso').aggregate(total=Sum('monto'))['total'] or 0
    movimientos = Movimiento.objects.select_related('evento').order_by('-fecha')
    balance_total = total_ingresos - total_egresos
    return render(request, 'tesoreria/balance.html', {
        'movimientos': movimientos,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance_total': balance_total
    })
