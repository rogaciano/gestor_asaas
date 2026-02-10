from django.contrib import admin
from .models import (
    Cliente, Recorrencia, ConfiguracaoFinanceira, Parceiro,
    FechamentoMensal, ComissaoIndicador, ComissaoSocio
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['name', 'cpfCnpj', 'email', 'phone', 'parceiro_indicador', 'synced_with_asaas', 'created_at']
    list_filter = ['synced_with_asaas', 'parceiro_indicador', 'created_at']
    search_fields = ['name', 'cpfCnpj', 'email']
    readonly_fields = ['asaas_id', 'created_at', 'updated_at']


@admin.register(Recorrencia)
class RecorrenciaAdmin(admin.ModelAdmin):
    list_display = ['description', 'cliente', 'value', 'cycle', 'status', 'next_due_date', 'synced_with_asaas']
    list_filter = ['status', 'cycle', 'billing_type', 'synced_with_asaas', 'created_at']
    search_fields = ['description', 'cliente__name']
    readonly_fields = ['asaas_id', 'created_at', 'updated_at']


@admin.register(ConfiguracaoFinanceira)
class ConfiguracaoFinanceiraAdmin(admin.ModelAdmin):
    list_display = ['percentual_seguranca_reserva', 'meses_media_reserva', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpfCnpj', 'tipo', 'percentual_comissao', 'majoritario', 'ativo', 'created_at']
    list_filter = ['tipo', 'ativo', 'majoritario']
    search_fields = ['nome', 'cpfCnpj', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FechamentoMensal)
class FechamentoMensalAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'total_receitas', 'total_despesas', 'resultado_liquido', 'valor_reserva', 'resultado_distribuivel', 'status']
    list_filter = ['status', 'ano']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComissaoIndicador)
class ComissaoIndicadorAdmin(admin.ModelAdmin):
    list_display = ['parceiro', 'cliente', 'valor_pagamento', 'percentual', 'valor_comissao', 'status', 'mes_referencia', 'ano_referencia']
    list_filter = ['status', 'parceiro', 'ano_referencia']
    search_fields = ['parceiro__nome', 'cliente__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComissaoSocio)
class ComissaoSocioAdmin(admin.ModelAdmin):
    list_display = ['parceiro', 'fechamento', 'resultado_distribuivel', 'percentual', 'valor_comissao', 'status']
    list_filter = ['status', 'parceiro']
    search_fields = ['parceiro__nome']
    readonly_fields = ['created_at', 'updated_at']

