from django.shortcuts import render
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from eventos.models import Evento
from ventas.models import Venta

@login_required
def inicio_dashboard(request):
    try:
        total_eventos = Evento.objects.count()
    except Exception:
        total_eventos = 0

    try:
        total_ventas = Venta.objects.count()
    except Exception:
        total_ventas = 0

    try:
        total_ganancias = Venta.objects.aggregate(
            total=Sum(F("cantidad") * F("precio_unitario_venta"))
        ).get("total") or 0
    except Exception:
        total_ganancias = 0

    try:
        gastos = Venta.objects.aggregate(
            gastos=Sum(F("precio_unitario_compra") * F("cantidad"))
        ).get("gastos") or 0
        ganancias_netas = total_ganancias - gastos
    except Exception:
        ganancias_netas = total_ganancias

    try:
        hoy = timezone.now()
        dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
        labels_dias = [d.strftime("%d/%m") for d in dias]
        data_dias = []
        for d in dias:
            siguiente = d + timedelta(days=1)
            total_dia = Venta.objects.filter(fecha_hora__range=(d, siguiente)).aggregate(
                total=Sum(F("cantidad") * F("precio_unitario_venta"))
            ).get("total") or 0
            data_dias.append(float(total_dia))
    except Exception:
        labels_dias = []
        data_dias = []

    try:
        productos_data = (
            Venta.objects.values("producto__nombre")
            .annotate(total=Sum("cantidad"))
            .order_by("-total")[:5]
        )
        labels_productos = [p.get("producto__nombre", "") for p in productos_data]
        data_productos = [p.get("total", 0) for p in productos_data]
    except Exception:
        labels_productos = []
        data_productos = []

    context = {
        "total_eventos": total_eventos,
        "total_ventas": total_ventas,
        "total_ganancias": total_ganancias,
        "ganancias_netas": ganancias_netas,
        "labels_dias": labels_dias,
        "data_dias": data_dias,
        "labels_productos": labels_productos,
        "data_productos": data_productos,
    }

    return render(request, "inicio.html", context)
