from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """Usuario del sistema (miembro del centro de estudiantes o visitante)."""
    nombre_completo = models.CharField(max_length=100)
    curso = models.CharField(max_length=20, blank=True, help_text="Curso o año del alumno")
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre_completo
