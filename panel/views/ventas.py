from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ventas.models import Producto, Venta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from collections import defaultdict
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from django.core.paginator import Paginator
import json

@login_required
def lista_productos(request):
    query = request.GET.get('q', '')
    order = request.GET.get('order', '')
    try:
        productos = Producto.objects.all()
        if query:
            productos = productos.filter(nombre__icontains=query)
        if order in ['stock', '-stock', 'precio_venta', '-precio_venta']:
            productos = productos.order_by(order)
    except Exception:
        productos = []
    context = {
        'productos': productos,
        'query': query,
        'order': order,
    }
    return render(request, 'ventas/productos.html', context)


@login_required
def historial_ventas(request):
    query = request.GET.get('q', '')
    medio = request.GET.get('medio', '')
    order = request.GET.get('order', '-fecha_hora')
    page = request.GET.get('page', 1)

    try:
        ventas = Venta.objects.select_related('producto', 'evento').all()
        if query:
            ventas = ventas.filter(producto__nombre__icontains=query)
        if medio:
            ventas = ventas.filter(medio_de_pago=medio)
        if order in ['fecha_hora', '-fecha_hora', 'precio_unitario_venta', '-precio_unitario_venta']:
            ventas = ventas.order_by(order)
    except Exception:
        ventas = []

    try:
        total_recaudado = sum(v.total() for v in ventas)
        total_efectivo = sum(v.total() for v in ventas if v.medio_de_pago == "Efectivo")
        total_mp = sum(v.total() for v in ventas if v.medio_de_pago == "Mercado Pago")
    except Exception:
        total_recaudado = total_efectivo = total_mp = 0

    eventos_data = defaultdict(float)
    try:
        for v in ventas:
            nombre_evento = v.evento.nombre if v.evento else "Sin evento"
            eventos_data[nombre_evento] += float(v.total())
    except Exception:
        eventos_data = defaultdict(float)

    paginator = Paginator(ventas, 20)
    try:
        page_obj = paginator.get_page(page)
    except Exception:
        page_obj = []

    if "export" in request.GET:
        try:
            wb = Workbook()
            ws_resumen = wb.active
            ws_resumen.title = "Resumen"

            header_fill = PatternFill(start_color="004085", end_color="004085", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            border = Border(
                left=Side(style="thin"), right=Side(style="thin"),
                top=Side(style="thin"), bottom=Side(style="thin")
            )

            ws_resumen.append(["Evento", "Total Recaudado ($)"])
            for cell in ws_resumen[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
                cell.border = border

            eventos_agg = ventas.values("evento__nombre").annotate(
                total=Sum(ExpressionWrapper(F("cantidad") * F("precio_unitario_venta"), output_field=DecimalField()))
            )

            for e in eventos_agg:
                ws_resumen.append([e["evento__nombre"] or "Sin evento", float(e["total"] or 0)])

            ws_resumen.append([])
            ws_resumen.append(["Total general", float(total_recaudado)])
            ws_resumen.column_dimensions["A"].width = 30
            ws_resumen.column_dimensions["B"].width = 20

            eventos_nombres = ventas.values_list("evento__nombre", flat=True).distinct()
            for nombre_evento in eventos_nombres:
                ws = wb.create_sheet(title=nombre_evento or "Sin evento")
                ws.append(["Producto", "Cantidad", "Medio de Pago", "Precio Unitario", "Total", "Fecha"])
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")
                    cell.border = border

                for venta in ventas.filter(evento__nombre=nombre_evento):
                    ws.append([
                        venta.producto.nombre,
                        venta.cantidad,
                        venta.medio_de_pago,
                        float(venta.precio_unitario_venta),
                        float(venta.total()),
                        venta.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                    ])
                for col in ["A", "B", "C", "D", "E", "F"]:
                    ws.column_dimensions[col].width = 20

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = f"Historial_Ventas_{request.user.username}.xlsx"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            wb.save(response)
            return response
        except Exception:
            pass

    context = {
        "ventas": page_obj,
        "query": query,
        "medio": medio,
        "order": order,
        "total_recaudado": total_recaudado,
        "total_efectivo": total_efectivo,
        "total_mp": total_mp,
        "page_obj": page_obj,
        "eventos_labels": json.dumps(list(eventos_data.keys())),
        "eventos_values": json.dumps(list(eventos_data.values())),
    }
    return render(request, "ventas/historial.html", context)
