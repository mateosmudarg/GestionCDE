from django.urls import path
from panel.views import ventas
urlpatterns = [
    path('productos/', ventas.lista_productos, name="lista_productos"),
    path('historial/', ventas.historial_ventas, name='historial_ventas'),
]
