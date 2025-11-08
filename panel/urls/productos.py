from django.urls import path
from panel.views import ventas

urlpatterns = [
    path('crear/', ventas.crear_producto, name='crear_producto'),
    path('<int:id>/editar/', ventas.editar_producto, name='editar_producto'),
    path('<int:id>/toggle-activo/', ventas.toggle_producto_activo, name='toggle_producto_activo'),
]
