"""
Script de diagnóstico para verificar diferenças no saldo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from asaas_app.models import Movimentacao
from django.db.models import Sum, Count
from decimal import Decimal

print("=" * 60)
print("DIAGNÓSTICO DE SALDO - COMPARAÇÃO ASAAS vs SISTEMA")
print("=" * 60)

# Análise geral
total_movimentacoes = Movimentacao.objects.count()
print(f"\n📊 Total de movimentações: {total_movimentacoes}")

# Por tipo
print("\n📋 Movimentações por tipo:")
por_tipo = Movimentacao.objects.values('tipo').annotate(
    total=Sum('valor'),
    quantidade=Count('id')
).order_by('tipo')

for item in por_tipo:
    print(f"  {item['tipo']}: {item['quantidade']} movimentações = R$ {item['total']:.2f}")

# Totais
receitas = Movimentacao.objects.filter(valor__gt=0).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
despesas = Movimentacao.objects.filter(valor__lt=0).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
saldo = receitas + despesas

print(f"\n💰 TOTAIS:")
print(f"  Receitas: R$ {receitas:.2f}")
print(f"  Despesas: R$ {abs(despesas):.2f}")
print(f"  Saldo: R$ {saldo:.2f}")

# Verificar se há movimentações sem sincronização
nao_sincronizadas = Movimentacao.objects.filter(synced_with_asaas=False).count()
print(f"\n⚠️  Movimentações não sincronizadas: {nao_sincronizadas}")

# Período das movimentações
primeira = Movimentacao.objects.order_by('data').first()
ultima = Movimentacao.objects.order_by('-data').first()

if primeira and ultima:
    print(f"\n📅 Período:")
    print(f"  Primeira movimentação: {primeira.data}")
    print(f"  Última movimentação: {ultima.data}")

# Verificar tipos específicos que podem estar faltando
print("\n🔍 Verificando tipos importantes:")
tipos_importantes = ['PAYMENT_FEE', 'TRANSFER_FEE', 'ANTICIPATION_FEE', 'CHARGEBACK', 'REFUND']
for tipo in tipos_importantes:
    count = Movimentacao.objects.filter(tipo=tipo).count()
    total = Movimentacao.objects.filter(tipo=tipo).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    print(f"  {tipo}: {count} movimentações = R$ {total:.2f}")

print("\n" + "=" * 60)
print("COMPARAÇÃO COM ASAAS:")
print("Saldo Asaas: R$ 2.247,20")
print(f"Saldo Sistema: R$ {saldo:.2f}")
print(f"Diferença: R$ {Decimal('2247.20') - saldo:.2f}")
print("=" * 60)
