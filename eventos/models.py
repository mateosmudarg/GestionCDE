from django.db import models
from cargos.models import Gestion

class Evento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    lugar = models.CharField(max_length=100, blank=True)
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name="eventos")
    recaudacion_total = models.FloatField(default=0.0)

    def actualizar_recaudacion(self):
        total_ganancia = sum(venta.ganancia() for venta in self.ventas.all())
        self.recaudacion_total = total_ganancia
        self.save(update_fields=["recaudacion_total"])

    def __str__(self):
        return self.nombre
