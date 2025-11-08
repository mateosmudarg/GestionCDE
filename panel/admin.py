from django.contrib import admin
from usuarios.models import Usuario
from cargos.models import Cargo, Gestion, MiembroGestion
from eventos.models import Evento
from tesoreria.models import Movimiento
from ventas.models import Producto, Venta

# =====================================
# 🧍 USUARIOS
# =====================================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "nombre_completo", "curso")
    search_fields = ("nombre_completo", "username")
    list_filter = ("curso",)
    ordering = ("nombre_completo",)
    fieldsets = (
        ("Información Personal", {
            "fields": ("nombre_completo", "curso", "telefono")
        }),
        ("Credenciales", {
            "fields": ("username", "password", "is_active", "is_staff", "is_superuser", "groups")
        }),
    )


# =====================================
# 🏛️ CARGOS Y GESTIÓN
# =====================================
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    ordering = ("nombre",)


@admin.register(Gestion)
class GestionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin")
    search_fields = ("nombre",)
    ordering = ("-fecha_inicio",)


@admin.register(MiembroGestion)
class MiembroGestionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cargo", "gestion")
    list_filter = ("cargo__nombre", "gestion__nombre")
    search_fields = ("usuario__nombre_completo",)
    ordering = ("gestion", "cargo")


# =====================================
# 🎉 EVENTOS
# =====================================
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha", "lugar", "gestion", "recaudacion_total")
    search_fields = ("nombre", "descripcion", "lugar")
    list_filter = ("gestion__nombre", "fecha")
    ordering = ("-fecha",)
    date_hierarchy = "fecha"


# =====================================
# 💵 TESORERÍA
# =====================================
@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "descripcion", "monto", "fecha", "evento")
    list_filter = ("tipo", "evento__nombre")
    search_fields = ("descripcion",)
    ordering = ("-fecha",)
    date_hierarchy = "fecha"


# =====================================
# 🛒 VENTAS
# =====================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "stock", "precio_compra", "precio_venta")
    search_fields = ("nombre",)
    list_filter = ("stock",)
    ordering = ("nombre",)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("producto", "cantidad", "medio_de_pago", "fecha_hora", "evento", "total_display")
    list_filter = ("medio_de_pago", "evento__nombre")
    date_hierarchy = "fecha_hora"
    search_fields = ("producto__nombre",)

    def total_display(self, obj):
        return f"${obj.total():.2f}"
    total_display.short_description = "Total"

    ordering = ("-fecha_hora",)
