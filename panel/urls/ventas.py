from django.urls import path
from panel.views import ventas
urlpatterns = [
    path('productos/', ventas.lista_productos, name="lista_productos"),
    path('historial/', ventas.historial_ventas, name='historial_ventas'),
    path('registrar/', ventas.registrar_ventas, name='registrar_ventas'),
    path('registrar/ajax/', ventas.registrar_venta_ajax, name='registrar_venta_ajax'),
    path('stock/', ventas.stock_actual, name='stock_actual'),
]
