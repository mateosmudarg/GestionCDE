from decimal import Decimal
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from ventas.models import Venta, Producto
from tesoreria.models import Movimiento
from eventos.models import Evento


# ---------- PRE SAVE ----------
@receiver(pre_save, sender=Venta)
def ajustar_stock_y_recaudacion_antes_guardar(sender, instance, **kwargs):
    """
    Antes de guardar una venta:
    - Si es nueva, descuenta stock.
    - Si es edición, ajusta diferencia de stock.
    - No toca tesorería todavía.
    """
    if instance.pk:
        try:
            prev = Venta.objects.get(pk=instance.pk)
        except ObjectDoesNotExist:
            prev = None
    else:
        prev = None

    # Si es nueva venta → reducir stock
    if prev is None:
        if instance.producto.stock < instance.cantidad:
            raise ValueError(f"Stock insuficiente para {instance.producto.nombre}. Disponible: {instance.producto.stock}")
        instance.producto.stock -= instance.cantidad
        instance.producto.save(update_fields=["stock"])
        return

    # Si se está editando
    if prev.producto_id != instance.producto_id:
        # Devolver stock al producto anterior
        prev.producto.stock += prev.cantidad
        prev.producto.save(update_fields=["stock"])

        # Descontar del nuevo producto
        if instance.producto.stock < instance.cantidad:
            raise ValueError(f"Stock insuficiente para {instance.producto.nombre}. Disponible: {instance.producto.stock}")
        instance.producto.stock -= instance.cantidad
        instance.producto.save(update_fields=["stock"])
    else:
        # Si cambió solo la cantidad
        diff = instance.cantidad - prev.cantidad
        if diff != 0:
            if diff > 0:  # vendió más
                if instance.producto.stock < diff:
                    raise ValueError(f"Stock insuficiente para aumentar cantidad de {instance.producto.nombre}")
                instance.producto.stock -= diff
            else:  # redujo la cantidad
                instance.producto.stock += abs(diff)
            instance.producto.save(update_fields=["stock"])


# ---------- POST SAVE ----------
@receiver(post_save, sender=Venta)
def crear_o_actualizar_movimiento_y_recaudacion(sender, instance, created, **kwargs):
    """
    Luego de guardar una venta:
    - Crea o actualiza el Movimiento en tesorería.
    - Actualiza recaudación_total del evento.
    """
    descripcion = f"Venta de {instance.producto.nombre} (venta_id={instance.id})"
    ganancia = Decimal(instance.total()) - (Decimal(instance.cantidad) * Decimal(instance.producto.precio_compra))

    # Buscar si ya existe el movimiento
    mov_qs = Movimiento.objects.filter(descripcion__icontains=f"venta_id={instance.id}")
    if mov_qs.exists():
        mov = mov_qs.first()
        mov.monto = ganancia
        mov.descripcion = descripcion
        mov.evento = instance.evento
        mov.save(update_fields=["monto", "descripcion", "evento"])
    else:
        Movimiento.objects.create(
            tipo="Ingreso",
            descripcion=descripcion,
            monto=ganancia,
            evento=instance.evento
        )

    # Actualizar la recaudación del evento
    if instance.evento:
        recaudacion_actual = getattr(instance.evento, "recaudacion_total", Decimal("0.00")) or Decimal("0.00")
        # Recalcular todas las ventas de este evento para mantener coherencia
        total_ganancia = sum(
            Decimal(v.total()) - (Decimal(v.cantidad) * Decimal(v.producto.precio_compra))
            for v in Venta.objects.filter(evento=instance.evento)
        )
        instance.evento.recaudacion_total = total_ganancia.quantize(Decimal("0.01"))
        instance.evento.save(update_fields=["recaudacion_total"])


# ---------- PRE DELETE ----------
@receiver(pre_delete, sender=Venta)
def devolver_stock_antes_de_eliminar(sender, instance, **kwargs):
    """Antes de eliminar una venta, devolver el stock al producto."""
    instance.producto.stock += instance.cantidad
    instance.producto.save(update_fields=["stock"])


# ---------- POST DELETE ----------
@receiver(post_delete, sender=Venta)
def eliminar_movimiento_y_actualizar_recaudacion(sender, instance, **kwargs):
    """Después de eliminar una venta, eliminar el movimiento y actualizar la recaudación."""
    Movimiento.objects.filter(descripcion__icontains=f"venta_id={instance.id}").delete()

    if instance.evento:
        total_ganancia = sum(
            Decimal(v.total()) - (Decimal(v.cantidad) * Decimal(v.producto.precio_compra))
            for v in Venta.objects.filter(evento=instance.evento)
        )
        # 🔹 Convertir explícitamente a Decimal antes de quantize()
        total_ganancia = Decimal(total_ganancia).quantize(Decimal("0.01"))
        instance.evento.recaudacion_total = total_ganancia
        instance.evento.save(update_fields=["recaudacion_total"])
