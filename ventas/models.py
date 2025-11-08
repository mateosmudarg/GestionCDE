from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist

from eventos.models import Evento
from tesoreria.models import Movimiento


class Producto(models.Model):
    """Productos que el centro puede vender."""
    nombre = models.CharField(max_length=50, help_text="Nombre del producto")
    stock = models.PositiveIntegerField(default=0, help_text="Stock disponible")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de compra por unidad")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de venta al público")

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    """Registro de una venta realizada en un evento.

    Notas:
    - Se guardan los precios unitarios en el momento de la venta (precio_unitario_venta / precio_unitario_compra)
        para mantener inmutables los cálculos históricos si cambian los precios del producto posteriormente.
    - Al crear/editar/eliminar una venta se ajusta `evento.recaudacion_total` con la diferencia de ganancia.
    - Se crea un Movimiento en tesorería con el monto bruto (cantidad * precio_unitario_venta).
    """
    MEDIO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Mercado Pago', 'Mercado Pago'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    medio_de_pago = models.CharField(max_length=20, choices=MEDIO_PAGO_CHOICES, default='Efectivo')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)

    precio_unitario_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    precio_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}u ({self.medio_de_pago})"

    # ----- cálculos -----
    def total(self) -> Decimal:
        """Total bruto (cantidad * precio de venta por unidad)."""
        if self.precio_unitario_venta is None:
            return Decimal('0.00')
        return (Decimal(self.cantidad) * self.precio_unitario_venta).quantize(Decimal('0.01'))

    def ganancia(self) -> Decimal:
        """Ganancia neta: cantidad * (precio_venta_unitario - precio_compra_unitario)."""
        if self.precio_unitario_venta is None or self.precio_unitario_compra is None:
            return Decimal('0.00')
        return (Decimal(self.cantidad) * (self.precio_unitario_venta - self.precio_unitario_compra)).quantize(Decimal('0.01'))

    # ----- guardado y sincronización con tesorería / evento -----
    def save(self, *args, **kwargs):
        """
        Guarda la venta fijando precios unitarios en caso de creación.
        La lógica de stock, movimientos y recaudación se maneja con signals.
        """
        if self.pk is None:
            # Solo al crear: fijar precios unitarios desde el producto
            self.precio_unitario_venta = self.producto.precio_venta
            self.precio_unitario_compra = self.producto.precio_unitario_compra
        super().save(*args, **kwargs)
