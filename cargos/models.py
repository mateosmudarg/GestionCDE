from django.db import models
from usuarios.models import Usuario

class Cargo(models.Model):
    """Define los cargos posibles dentro del centro."""
    CARGOS_CHOICES = [
        ('Presidente', 'Presidente'),
        ('Vicepresidente', 'Vicepresidente'),
        ('Secretario', 'Secretario'),
        ('Tesorero', 'Tesorero'),
        ('Vocal', 'Vocal'),
    ]
    nombre = models.CharField(max_length=50, choices=CARGOS_CHOICES, unique=True)

    def __str__(self):
        return self.nombre

class Gestion(models.Model):
    """Representa un periodo de gestión del centro."""
    nombre = models.CharField(max_length=100, help_text="Ejemplo: Gestión 2025")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class MiembroGestion(models.Model):
    """Asocia un usuario a un cargo durante una gestión específica."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'cargo', 'gestion')

    def __str__(self):
        return f"{self.usuario} - {self.cargo} ({self.gestion})"
