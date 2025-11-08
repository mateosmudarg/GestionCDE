from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ventas.models import Producto, Venta
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import csrf_exempt
from eventos.models import Evento
from tesoreria.models import Movimiento
from django.db import transaction
from decimal import Decimal
from openpyxl import Workbook
@login_required
def historial_ventas(request):
    query = request.GET.get('q', '')
    medio = request.GET.get('medio', '')
    order = request.GET.get('order', '-fecha_hora')
    page = request.GET.get('page', 1)

    ventas = Venta.objects.select_related('producto', 'evento').all()
    
    if query:
        ventas = ventas.filter(producto__nombre__icontains=query)
    if medio:
        ventas = ventas.filter(medio_de_pago=medio)
    if order in ['fecha_hora', '-fecha_hora', 'precio_unitario_venta', '-precio_unitario_venta']:
        ventas = ventas.order_by(order)

    total_recaudado = sum(v.total() for v in ventas)
    total_efectivo = sum(v.total() for v in ventas if v.medio_de_pago == "Efectivo")
    total_mp = sum(v.total() for v in ventas if v.medio_de_pago == "Mercado Pago")

    eventos_data = {}
    for v in ventas:
        nombre_evento = v.evento.nombre if v.evento else "Sin evento"
        eventos_data[nombre_evento] = eventos_data.get(nombre_evento, 0) + float(v.total())

    paginator = Paginator(ventas, 20)
    page_obj = paginator.get_page(page)

    if "export" in request.GET:
        wb = Workbook()
        ws_resumen = wb.active
        ws_resumen.title = "Resumen"
        ws_resumen.append(["Evento", "Total Recaudado ($)"])
        
        eventos_agg = ventas.values("evento__nombre").annotate(
            total=Sum('venta__total')
        )
        for e in eventos_agg:
            ws_resumen.append([e["evento__nombre"] or "Sin evento", float(e["total"] or 0)])
        
        ws_resumen.append([])
        ws_resumen.append(["Total general", float(total_recaudado)])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"Historial_Ventas_{request.user.username}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

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

@login_required
def registrar_ventas(request):
    productos = Producto.objects.annotate(
        total_vendido=Sum('venta__cantidad')
    ).order_by('-total_vendido', 'nombre')

    eventos = Evento.objects.order_by('fecha')

    return render(request, 'ventas/registrar_ventas.html', {
        'productos': productos,
        'eventos': eventos
    })

@login_required
@csrf_exempt
def registrar_venta_ajax(request):
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('producto_id')
            cantidad = int(request.POST.get('cantidad', 1))
            medio_de_pago = request.POST.get('medio_de_pago', 'Efectivo')
            evento_id = request.POST.get('evento_id') or None

            if cantidad <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'La cantidad debe ser mayor a 0'
                }, status=400)

            with transaction.atomic():
                # Bloquea el registro para evitar condiciones de carrera
                producto = Producto.objects.select_for_update().get(pk=producto_id)
                
                # Validación exhaustiva
                if producto.stock < cantidad:
                    return JsonResponse({
                        'success': False,
                        'error': f'Stock insuficiente. Disponible: {producto.stock}, Solicitado: {cantidad}'
                    }, status=400)

                if not producto.activo:
                    return JsonResponse({
                        'success': False,
                        'error': 'El producto no está activo'
                    }, status=400)

                # Crear venta
                venta = Venta.objects.create(
                    producto=producto,
                    cantidad=cantidad,
                    medio_de_pago=medio_de_pago,
                    evento_id=evento_id,
                    precio_unitario_venta=producto.precio_venta,
                    precio_unitario_compra=producto.precio_compra
                )
                
                # Actualizar stock de manera segura
                producto.stock = producto.stock - cantidad
                producto.save()

                # Registrar movimiento en tesorería
                Movimiento.objects.create(
                    tipo='Ingreso',
                    descripcion=f'Venta de {cantidad} x {producto.nombre}',
                    monto=venta.total(),
                    evento_id=evento_id
                )

            return JsonResponse({
                'success': True,
                'venta': {
                    'producto': producto.nombre,
                    'cantidad': cantidad,
                    'total': str(venta.total()),
                    'medio_de_pago': medio_de_pago,
                    'stock_restante': producto.stock
                }
            })

        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado.'}, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar la venta: {str(e)}'
            }, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@login_required
def stock_actual(request):
    productos = Producto.objects.all().values('id', 'stock')
    return JsonResponse(list(productos), safe=False)

@login_required
def lista_productos(request):
    query = request.GET.get('q', '')
    order = request.GET.get('order', 'nombre')
    estado = request.GET.get('estado', 'todos')
    
    productos = Producto.objects.all()
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    if estado == 'activos':
        productos = productos.filter(activo=True)
    elif estado == 'inactivos':
        productos = productos.filter(activo=False)
    
    if order in ['nombre', '-nombre', 'stock', '-stock', 'precio_venta', '-precio_venta', 
                'precio_compra', '-precio_compra', 'fecha_creacion', '-fecha_creacion']:
        productos = productos.order_by(order)
    
    productos = productos.annotate(
        total_vendido=Sum('venta__cantidad'),
        total_ventas=Count('venta')
    )

    paginator = Paginator(productos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_productos = productos.count()
    productos_activos = productos.filter(activo=True).count()
    stock_total = sum(p.stock for p in productos)
    valor_inventario_total = sum(p.valor_inventario for p in productos)

    context = {
        'productos': page_obj,
        'query': query,
        'order': order,
        'estado': estado,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'stock_total': stock_total,
        'valor_inventario_total': valor_inventario_total,
    }
    return render(request, 'ventas/productos.html', context)

@login_required
def crear_producto(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            stock = int(request.POST.get('stock', 0))
            precio_compra = Decimal(request.POST.get('precio_compra', 0))
            precio_venta = Decimal(request.POST.get('precio_venta', 0))
            
            if precio_venta < precio_compra:
                return JsonResponse({
                    'success': False,
                    'error': 'El precio de venta no puede ser menor al precio de compra'
                })
            
            with transaction.atomic():
                producto = Producto.objects.create(
                    nombre=nombre,
                    stock=stock,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta
                )
                
                if stock > 0 and precio_compra > 0:
                    Movimiento.objects.create(
                        tipo='Egreso',
                        descripcion=f'Compra de stock inicial: {nombre}',
                        monto=stock * precio_compra,
                        evento=None
                    )
            
            return JsonResponse({
                'success': True,
                'message': 'Producto creado exitosamente',
                'producto_id': producto.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al crear producto: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            stock = int(request.POST.get('stock', 0))
            precio_compra = Decimal(request.POST.get('precio_compra', 0))
            precio_venta = Decimal(request.POST.get('precio_venta', 0))
            activo = request.POST.get('activo') == 'true'
            
            if precio_venta < precio_compra:
                return JsonResponse({
                    'success': False,
                    'error': 'El precio de venta no puede ser menor al precio de compra'
                })
            
            producto.nombre = nombre
            producto.stock = stock
            producto.precio_compra = precio_compra
            producto.precio_venta = precio_venta
            producto.activo = activo
            producto.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Producto actualizado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al actualizar producto: {str(e)}'
            })
    
    return JsonResponse({
        'success': True,
        'producto': {
            'id': producto.id,
            'nombre': producto.nombre,
            'stock': producto.stock,
            'precio_compra': float(producto.precio_compra),
            'precio_venta': float(producto.precio_venta),
            'activo': producto.activo,
            'margen_ganancia': float(producto.margen_ganancia),
            'ganancia_unitaria': float(producto.ganancia_unitaria),
            'valor_inventario': float(producto.valor_inventario)
        }
    })

@login_required
def toggle_producto_activo(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        try:
            producto.activo = not producto.activo
            producto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Producto {"activado" if producto.activo else "desactivado"} exitosamente',
                'activo': producto.activo
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al cambiar estado: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

