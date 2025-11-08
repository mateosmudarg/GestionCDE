from django.urls import path
from panel.views import tesoreria
urlpatterns = [
    path('', tesoreria.balance, name="balance_tesoreria"),
    path('ingresos/', tesoreria.ingresos, name='ingresos_tesoreria'),
    path('egresos/', tesoreria.egresos, name='egresos_tesoreria'),
]
