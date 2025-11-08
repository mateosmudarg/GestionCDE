from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from panel.views import inicio

urlpatterns = [
    path('eventos/', include('panel.urls.eventos')),
    path('ventas/', include('panel.urls.ventas')),
    path('', inicio.inicio_dashboard, name='inicio_dashboard'),
    path('tesoreria/', include('panel.urls.tesoreria')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
