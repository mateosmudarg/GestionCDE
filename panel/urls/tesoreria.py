from django.urls import path
from panel.views import tesoreria
urlpatterns = [
    path('', tesoreria.balance_tesoreria, name="balance_tesoreria"),
    path('ingresos/', tesoreria.ingresos_tesoreria, name='ingresos_tesoreria'),
    path('egresos/', tesoreria.egresos_tesoreria, name='egresos_tesoreria'),
]
