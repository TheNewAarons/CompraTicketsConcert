from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'tipo_entrada', 'numero_asiento', 'estado', 'fecha_compra']
    list_filter = ['estado', 'tipo_entrada']
    search_fields = ['nombre', 'email', 'dni']
    actions = ['marcar_como_verificado', 'marcar_como_rechazado']

    def marcar_como_verificado(self, request, queryset):
        queryset.update(estado='VERIFICADO')
    marcar_como_verificado.short_description = "Marcar tickets seleccionados como verificados"

    def marcar_como_rechazado(self, request, queryset):
        queryset.update(estado='RECHAZADO')
    marcar_como_rechazado.short_description = "Marcar tickets seleccionados como rechazados"
