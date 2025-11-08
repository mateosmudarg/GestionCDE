from django.urls import path
from panel.views import eventos
urlpatterns = [
    path('', eventos.lista_eventos, name="eventos_lista"),
    path('calendario/', eventos.calendario_eventos, name='calendario_eventos'),
    path('detalles/<int:id>/', eventos.detalles_evento, name='evento_detalles'),
]
