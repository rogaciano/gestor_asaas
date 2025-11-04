from django.contrib import admin
from .models import Cliente, Recorrencia


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['name', 'cpfCnpj', 'email', 'phone', 'synced_with_asaas', 'created_at']
    list_filter = ['synced_with_asaas', 'created_at']
    search_fields = ['name', 'cpfCnpj', 'email']
    readonly_fields = ['asaas_id', 'created_at', 'updated_at']


@admin.register(Recorrencia)
class RecorrenciaAdmin(admin.ModelAdmin):
    list_display = ['description', 'cliente', 'value', 'cycle', 'status', 'next_due_date', 'synced_with_asaas']
    list_filter = ['status', 'cycle', 'billing_type', 'synced_with_asaas', 'created_at']
    search_fields = ['description', 'cliente__name']
    readonly_fields = ['asaas_id', 'created_at', 'updated_at']

