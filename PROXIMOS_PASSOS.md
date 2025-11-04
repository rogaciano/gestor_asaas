# 🚀 Próximos Passos - Melhorias Futuras

## 📋 Roadmap de Funcionalidades

Este documento contém as próximas funcionalidades a serem implementadas após os testes iniciais do sistema financeiro.

---

## 1️⃣ Exportação de Relatórios (PDF/Excel)

### 📊 Objetivo
Permitir exportar relatórios em formatos PDF e Excel para compartilhamento e arquivamento.

### 🔧 Tecnologias
- **PDF**: `WeasyPrint` ou `ReportLab`
- **Excel**: `openpyxl` ou `xlsxwriter`
- **CSV**: Nativo do Python (pandas)

### 📝 Implementação

#### Instalação
```bash
pip install weasyprint openpyxl pandas
```

#### Views a Criar
```python
# asaas_app/views.py

from django.http import HttpResponse
from openpyxl import Workbook
from weasyprint import HTML
import pandas as pd

@login_required(login_url='login')
def export_relatorio_excel(request):
    """Exporta relatório para Excel"""
    # Pega parâmetros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Busca movimentações
    movimentacoes = Movimentacao.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim
    ).select_related('cliente', 'plano_contas')
    
    # Cria workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Movimentações"
    
    # Cabeçalhos
    headers = ['Data', 'Descrição', 'Cliente', 'Categoria', 'Valor', 'Status']
    ws.append(headers)
    
    # Dados
    for mov in movimentacoes:
        ws.append([
            mov.data.strftime('%d/%m/%Y'),
            mov.descricao,
            mov.cliente.name if mov.cliente else '-',
            mov.plano_contas.nome if mov.plano_contas else '-',
            float(mov.valor),
            mov.get_status_conciliacao_display()
        ])
    
    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=relatorio_{data_inicio}_{data_fim}.xlsx'
    wb.save(response)
    
    return response


@login_required(login_url='login')
def export_relatorio_pdf(request):
    """Exporta relatório para PDF"""
    # Pega dados (similar ao relatório HTML)
    context = get_relatorio_context(request)
    
    # Renderiza template
    html_string = render_to_string('financeiro/relatorio_pdf.html', context)
    
    # Converte para PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=relatorio.pdf'
    
    return response
```

#### URLs a Adicionar
```python
# asaas_app/urls.py
path('financeiro/relatorios/export/excel/', views.export_relatorio_excel, name='export_relatorio_excel'),
path('financeiro/relatorios/export/pdf/', views.export_relatorio_pdf, name='export_relatorio_pdf'),
path('financeiro/relatorios/export/csv/', views.export_relatorio_csv, name='export_relatorio_csv'),
```

#### Templates
```html
<!-- Adicionar botões na página de relatórios -->
<div class="flex gap-3">
    <a href="{% url 'export_relatorio_excel' %}?data_inicio={{ data_inicio }}&data_fim={{ data_fim }}"
       class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
        <i class="fas fa-file-excel mr-2"></i> Exportar Excel
    </a>
    <a href="{% url 'export_relatorio_pdf' %}?data_inicio={{ data_inicio }}&data_fim={{ data_fim }}"
       class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
        <i class="fas fa-file-pdf mr-2"></i> Exportar PDF
    </a>
</div>
```

### ⏱️ Estimativa
**2-3 horas** de implementação

---

## 2️⃣ Gráficos Interativos (Chart.js)

### 📊 Objetivo
Adicionar gráficos interativos para melhor visualização dos dados financeiros.

### 🔧 Tecnologia
- **Chart.js 4.x** (biblioteca JavaScript)

### 📝 Implementação

#### CDN a Adicionar
```html
<!-- templates/base.html -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
```

#### Template de Relatório
```html
<!-- templates/financeiro/relatorios.html -->

<!-- Gráfico de Pizza - Receitas vs Despesas -->
<div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Receitas vs Despesas</h2>
    <canvas id="receitasDespesasChart" width="400" height="200"></canvas>
</div>

<!-- Gráfico de Linha - Evolução Mensal -->
<div class="bg-white shadow rounded-lg p-6 mt-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Evolução Mensal</h2>
    <canvas id="evolucaoMensalChart" width="400" height="200"></canvas>
</div>

<!-- Gráfico de Barras - Por Categoria -->
<div class="bg-white shadow rounded-lg p-6 mt-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Top Categorias</h2>
    <canvas id="categoriaChart" width="400" height="300"></canvas>
</div>

<script>
// Gráfico de Pizza
const ctxPizza = document.getElementById('receitasDespesasChart').getContext('2d');
new Chart(ctxPizza, {
    type: 'pie',
    data: {
        labels: ['Receitas', 'Despesas'],
        datasets: [{
            data: [{{ total_receitas }}, {{ total_despesas }}],
            backgroundColor: ['#10b981', '#ef4444'],
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom',
            }
        }
    }
});

// Gráfico de Linha
const ctxLinha = document.getElementById('evolucaoMensalChart').getContext('2d');
new Chart(ctxLinha, {
    type: 'line',
    data: {
        labels: [{% for item in por_mes %}'{{ item.mes|date:"m/Y" }}'{% if not forloop.last %},{% endif %}{% endfor %}],
        datasets: [{
            label: 'Receitas',
            data: [{% for item in por_mes %}{{ item.receitas|default:0 }}{% if not forloop.last %},{% endif %}{% endfor %}],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4
        }, {
            label: 'Despesas',
            data: [{% for item in por_mes %}{{ item.despesas|default:0 }}{% if not forloop.last %},{% endif %}{% endfor %}],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom',
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Gráfico de Barras
const ctxBarra = document.getElementById('categoriaChart').getContext('2d');
new Chart(ctxBarra, {
    type: 'bar',
    data: {
        labels: [{% for item in por_categoria|slice:":10" %}'{{ item.plano_contas__nome }}'{% if not forloop.last %},{% endif %}{% endfor %}],
        datasets: [{
            label: 'Valor',
            data: [{% for item in por_categoria|slice:":10" %}{{ item.total }}{% if not forloop.last %},{% endif %}{% endfor %}],
            backgroundColor: '#3b82f6',
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
</script>
```

### ⏱️ Estimativa
**1-2 horas** de implementação

---

## 3️⃣ Webhooks do Asaas (Sincronização em Tempo Real)

### 📊 Objetivo
Receber notificações do Asaas automaticamente quando houver novos pagamentos, cobranças, etc.

### 🔧 Tecnologia
- **Django REST Framework** (para criar API de webhook)
- **Celery** (para processamento assíncrono - opcional)

### 📝 Implementação

#### Instalação
```bash
pip install djangorestframework
```

#### Settings
```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]

# Webhook Secret (configurar no Asaas)
ASAAS_WEBHOOK_SECRET = config('ASAAS_WEBHOOK_SECRET', default='')
```

#### View do Webhook
```python
# asaas_app/views.py

import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def asaas_webhook(request):
    """Recebe webhooks do Asaas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Valida assinatura (segurança)
        signature = request.headers.get('asaas-access-token')
        if signature != settings.ASAAS_WEBHOOK_SECRET:
            logger.warning('Webhook inválido - assinatura incorreta')
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        # Parse do payload
        payload = json.loads(request.body)
        event = payload.get('event')
        
        # Processa evento
        if event == 'PAYMENT_RECEIVED':
            processar_pagamento_recebido(payload)
        elif event == 'PAYMENT_CREATED':
            processar_pagamento_criado(payload)
        elif event == 'SUBSCRIPTION_CREATED':
            processar_assinatura_criada(payload)
        # ... outros eventos
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f'Erro no webhook: {str(e)}')
        return JsonResponse({'error': 'Internal error'}, status=500)


def processar_pagamento_recebido(payload):
    """Processa pagamento recebido"""
    payment_data = payload.get('payment', {})
    
    # Cria movimentação
    Movimentacao.objects.create(
        asaas_id=payment_data['id'],
        data=payment_data['paymentDate'],
        descricao=f"Pagamento recebido - {payment_data['description']}",
        tipo='PAYMENT',
        valor=payment_data['value'],
        dados_asaas=payment_data,
        synced_with_asaas=True
    )
    
    # Aplica regras de categorização
    mov = Movimentacao.objects.get(asaas_id=payment_data['id'])
    aplicar_regras_categorizacao(mov)
    
    logger.info(f'Pagamento {payment_data["id"]} processado via webhook')
```

#### URL
```python
# asaas_app/urls.py
path('webhook/asaas/', views.asaas_webhook, name='asaas_webhook'),
```

#### Configuração no Asaas
1. Acesse: https://www.asaas.com/webhooks
2. Adicione a URL: `https://seu-dominio.com/webhook/asaas/`
3. Selecione eventos:
   - Pagamento recebido
   - Pagamento criado
   - Cobrança vencida
   - Assinatura criada
   - etc.
4. Copie o token e adicione no `.env`:
   ```
   ASAAS_WEBHOOK_SECRET=seu_token_aqui
   ```

### ⏱️ Estimativa
**3-4 horas** de implementação

---

## 4️⃣ Alertas por Email (Movimentações Não Conciliadas)

### 📊 Objetivo
Enviar emails automáticos quando houver movimentações não conciliadas.

### 🔧 Tecnologia
- **Django Email** (SMTP)
- **Celery + Redis** (para agendamento)

### 📝 Implementação

#### Settings
```python
# config/settings.py

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@asaas.com')

# Destinatários de alertas
ALERT_EMAILS = config('ALERT_EMAILS', default='admin@asaas.com', cast=lambda v: [s.strip() for s in v.split(',')])
```

#### Comando de Verificação
```python
# asaas_app/management/commands/verificar_conciliacao.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from asaas_app.models import Movimentacao

class Command(BaseCommand):
    help = 'Verifica movimentações não conciliadas e envia alertas'

    def handle(self, *args, **options):
        # Busca não conciliadas
        nao_conciliadas = Movimentacao.objects.filter(
            status_conciliacao='NAO_CONCILIADO'
        )
        
        quantidade = nao_conciliadas.count()
        
        if quantidade == 0:
            self.stdout.write(self.style.SUCCESS('Tudo conciliado!'))
            return
        
        # Calcula valor total
        total = sum([mov.valor for mov in nao_conciliadas])
        
        # Monta mensagem
        mensagem = f"""
        Olá!
        
        Você possui {quantidade} movimentação(ões) não conciliada(s):
        
        Valor total: R$ {total:.2f}
        
        Detalhes:
        """
        
        for mov in nao_conciliadas[:10]:  # Primeiras 10
            mensagem += f"\n- {mov.data.strftime('%d/%m/%Y')}: {mov.descricao} - R$ {mov.valor:.2f}"
        
        if quantidade > 10:
            mensagem += f"\n\n... e mais {quantidade - 10} movimentações."
        
        mensagem += "\n\nAcesse o sistema para conciliar: https://seu-dominio.com/financeiro/conciliacao/"
        
        # Envia email
        send_mail(
            subject=f'[Asaas Manager] {quantidade} movimentações não conciliadas',
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ALERT_EMAILS,
            fail_silently=False,
        )
        
        self.stdout.write(self.style.SUCCESS(f'Email enviado para {len(settings.ALERT_EMAILS)} destinatário(s)'))
```

#### Agendamento (Celery - Opcional)
```python
# config/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('asaas_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tarefas agendadas
app.conf.beat_schedule = {
    'verificar-conciliacao-diaria': {
        'task': 'asaas_app.tasks.verificar_conciliacao',
        'schedule': crontab(hour=9, minute=0),  # Todo dia às 9h
    },
}

# asaas_app/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def verificar_conciliacao():
    call_command('verificar_conciliacao')
```

#### Agendamento Manual (Cron)
```bash
# Adicionar ao crontab
# crontab -e

# Todo dia às 9h
0 9 * * * cd /caminho/projeto && /caminho/venv/bin/python manage.py verificar_conciliacao
```

### ⏱️ Estimativa
**2-3 horas** de implementação

---

## 5️⃣ Orçamento e Planejamento (Metas por Categoria)

### 📊 Objetivo
Permitir criar metas/orçamentos por categoria e acompanhar o cumprimento.

### 🔧 Implementação

#### Modelo
```python
# asaas_app/models.py

class Orcamento(models.Model):
    """Orçamento/Meta por categoria"""
    
    plano_contas = models.ForeignKey(
        PlanoContas,
        on_delete=models.CASCADE,
        related_name='orcamentos',
        verbose_name='Categoria'
    )
    mes_ano = models.DateField('Mês/Ano')
    valor_planejado = models.DecimalField('Valor Planejado', max_digits=10, decimal_places=2)
    valor_realizado = models.DecimalField('Valor Realizado', max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField('Observações', blank=True, null=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        db_table = 'orcamentos'
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        unique_together = ['plano_contas', 'mes_ano']
    
    def __str__(self):
        return f"{self.plano_contas.nome} - {self.mes_ano.strftime('%m/%Y')}"
    
    @property
    def percentual_realizado(self):
        """Percentual do orçamento realizado"""
        if self.valor_planejado == 0:
            return 0
        return (self.valor_realizado / self.valor_planejado) * 100
    
    @property
    def status(self):
        """Status do orçamento"""
        perc = self.percentual_realizado
        if perc < 80:
            return 'DENTRO'
        elif perc < 100:
            return 'ATENCAO'
        else:
            return 'EXCEDIDO'
    
    def atualizar_realizado(self):
        """Atualiza valor realizado com base nas movimentações"""
        inicio_mes = self.mes_ano.replace(day=1)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        movimentacoes = Movimentacao.objects.filter(
            plano_contas=self.plano_contas,
            data__gte=inicio_mes,
            data__lte=fim_mes
        )
        
        self.valor_realizado = sum([mov.valor for mov in movimentacoes])
        self.save()
```

#### Form
```python
# asaas_app/forms.py

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['plano_contas', 'mes_ano', 'valor_planejado', 'observacoes']
        widgets = {
            'plano_contas': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'mes_ano': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'type': 'month'
            }),
            'valor_planejado': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'step': '0.01'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 3
            }),
        }
```

#### Views
```python
# asaas_app/views.py

@login_required(login_url='login')
def orcamento_list(request):
    """Lista orçamentos"""
    mes_ano = request.GET.get('mes_ano', datetime.now().strftime('%Y-%m'))
    
    orcamentos = Orcamento.objects.filter(
        mes_ano__startswith=mes_ano
    ).select_related('plano_contas')
    
    # Atualiza valores realizados
    for orc in orcamentos:
        orc.atualizar_realizado()
    
    context = {
        'orcamentos': orcamentos,
        'mes_ano': mes_ano,
    }
    return render(request, 'financeiro/orcamento_list.html', context)


@login_required(login_url='login')
def orcamento_create(request):
    """Cria orçamento"""
    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orçamento criado com sucesso!')
            return redirect('orcamento_list')
    else:
        form = OrcamentoForm()
    
    return render(request, 'financeiro/orcamento_form.html', {'form': form})
```

#### Template
```html
<!-- templates/financeiro/orcamento_list.html -->
{% extends 'base.html' %}

{% block content %}
<div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Orçamentos e Metas</h1>
    <p class="mt-2 text-gray-600">Acompanhe o cumprimento das metas por categoria</p>
</div>

<!-- Filtro de Mês -->
<div class="mb-6 bg-white shadow rounded-lg p-6">
    <form method="get" class="flex gap-4 items-end">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mês/Ano</label>
            <input type="month" name="mes_ano" value="{{ mes_ano }}"
                   class="px-4 py-2 border border-gray-300 rounded-lg">
        </div>
        <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Filtrar
        </button>
    </form>
</div>

<!-- Lista de Orçamentos -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for orc in orcamentos %}
    <div class="bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-semibold text-gray-900">{{ orc.plano_contas.nome }}</h3>
            <span class="px-2 py-1 text-xs rounded 
                {% if orc.status == 'DENTRO' %}bg-green-100 text-green-800
                {% elif orc.status == 'ATENCAO' %}bg-yellow-100 text-yellow-800
                {% else %}bg-red-100 text-red-800{% endif %}">
                {{ orc.status }}
            </span>
        </div>
        
        <div class="space-y-2 mb-4">
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">Planejado:</span>
                <span class="font-medium">R$ {{ orc.valor_planejado|floatformat:2 }}</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">Realizado:</span>
                <span class="font-medium">R$ {{ orc.valor_realizado|floatformat:2 }}</span>
            </div>
        </div>
        
        <!-- Barra de Progresso -->
        <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div class="h-2 rounded-full 
                {% if orc.percentual_realizado < 80 %}bg-green-600
                {% elif orc.percentual_realizado < 100 %}bg-yellow-600
                {% else %}bg-red-600{% endif %}"
                 style="width: {{ orc.percentual_realizado|floatformat:0 }}%"></div>
        </div>
        <p class="text-xs text-gray-500 text-center">{{ orc.percentual_realizado|floatformat:1 }}%</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

#### URLs
```python
# asaas_app/urls.py
path('financeiro/orcamentos/', views.orcamento_list, name='orcamento_list'),
path('financeiro/orcamentos/novo/', views.orcamento_create, name='orcamento_create'),
path('financeiro/orcamentos/<int:pk>/editar/', views.orcamento_edit, name='orcamento_edit'),
path('financeiro/orcamentos/<int:pk>/deletar/', views.orcamento_delete, name='orcamento_delete'),
```

### ⏱️ Estimativa
**4-5 horas** de implementação

---

## 📅 Ordem de Implementação Recomendada

### Fase 1 - Rápidas e Impactantes
1. **Gráficos Interativos** (1-2h) ⭐ Alta prioridade
2. **Exportação de Relatórios** (2-3h) ⭐ Alta prioridade

### Fase 2 - Automação
3. **Alertas por Email** (2-3h) ⭐ Média prioridade
4. **Webhooks do Asaas** (3-4h) ⭐ Média prioridade

### Fase 3 - Planejamento
5. **Orçamento e Metas** (4-5h) ⭐ Baixa prioridade (pode esperar feedback dos usuários)

---

## 📦 Dependências Adicionais

Adicionar ao `requirements.txt`:

```txt
# Exportação
weasyprint==60.1
openpyxl==3.1.2
pandas==2.1.3

# API/Webhooks
djangorestframework==3.14.0

# Tarefas Assíncronas (Opcional)
celery==5.3.4
redis==5.0.1
django-celery-beat==2.5.0
```

---

## 🎯 Considerações Finais

### Antes de Implementar
- ✅ Testar sistema atual completamente
- ✅ Coletar feedback dos usuários
- ✅ Priorizar com base nas necessidades reais

### Durante a Implementação
- ✅ Criar branch separada para cada funcionalidade
- ✅ Testar isoladamente antes de merge
- ✅ Atualizar documentação

### Após Implementação
- ✅ Adicionar ao guia do usuário
- ✅ Criar changelog
- ✅ Treinar usuários

---

**Desenvolvido por: [Seu Nome]**  
**Data: Novembro 2025**  
**Versão: 1.0**

