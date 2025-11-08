from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from panel.views import inicio

urlpatterns = [
    path('eventos/', include('panel.urls.eventos')),
    path('ventas/', include('panel.urls.ventas')),
    path('', inicio.dashboard_inicio, name='inicio_dashboard'),
    path('tesoreria/', include('panel.urls.tesoreria')),
    path('productos/', include('panel.urls.productos')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
