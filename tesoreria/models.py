from django.db import models
from eventos.models import Evento

class Movimiento(models.Model):
    """Movimiento económico: ingreso o egreso."""
    TIPO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo}: ${self.monto} - {self.descripcion}"

    class Meta:
        ordering = ['-fecha']
