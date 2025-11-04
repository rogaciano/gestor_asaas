from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from .models import Cliente, Recorrencia, PlanoContas, Movimentacao, RegraCategorizacao
from .forms import ClienteForm, RecorrenciaForm, PlanoContasForm, MovimentacaoForm, RegraCategorizacaoForm
from .services import AsaasService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ==================== AUTENTICAÇÃO ====================

def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """View de logout"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')


# ==================== HOME ====================

@login_required(login_url='login')
def home(request):
    """Página inicial com estatísticas"""
    total_clientes = Cliente.objects.count()
    total_recorrencias = Recorrencia.objects.count()
    recorrencias_ativas = Recorrencia.objects.filter(status='ACTIVE').count()
    clientes_sincronizados = Cliente.objects.filter(synced_with_asaas=True).count()
    
    context = {
        'total_clientes': total_clientes,
        'total_recorrencias': total_recorrencias,
        'recorrencias_ativas': recorrencias_ativas,
        'clientes_sincronizados': clientes_sincronizados,
    }
    return render(request, 'home.html', context)


# ==================== CLIENTES ====================

@login_required(login_url='login')
def cliente_list(request):
    """Lista todos os clientes com filtros e pesquisa"""
    clientes = Cliente.objects.all()
    
    # Pesquisa por nome, email ou CPF/CNPJ
    search_query = request.GET.get('search', '').strip()
    if search_query:
        clientes = clientes.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(cpfCnpj__icontains=search_query)
        )
    
    # Filtro por tipo de pessoa (baseado no tamanho do CPF/CNPJ)
    tipo_pessoa = request.GET.get('tipo_pessoa', '')
    if tipo_pessoa == 'fisica':
        # CPF: filtra por documentos que não contém "/" (característico de CNPJ)
        clientes = clientes.exclude(cpfCnpj__contains='/')
    elif tipo_pessoa == 'juridica':
        # CNPJ: filtra por documentos que contém "/" (formato CNPJ)
        clientes = clientes.filter(cpfCnpj__contains='/')
    
    # Filtro por sincronização
    sync_status = request.GET.get('sync_status', '')
    if sync_status == 'synced':
        clientes = clientes.filter(synced_with_asaas=True)
    elif sync_status == 'not_synced':
        clientes = clientes.filter(synced_with_asaas=False)
    
    # Ordenação
    clientes = clientes.order_by('-created_at')
    
    context = {
        'clientes': clientes,
        'search_query': search_query,
        'tipo_pessoa': tipo_pessoa,
        'sync_status': sync_status,
    }
    return render(request, 'clientes/list.html', context)


@login_required(login_url='login')
def cliente_create(request):
    """Cria um novo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            
            # Tenta criar o cliente no Asaas
            asaas_service = AsaasService()
            customer_data = {
                'name': cliente.name,
                'cpfCnpj': cliente.cpfCnpj,
                'email': cliente.email,
                'phone': cliente.phone or '',
                'mobilePhone': cliente.mobilePhone or '',
                'address': cliente.address or '',
                'addressNumber': cliente.addressNumber or '',
                'complement': cliente.complement or '',
                'province': cliente.province or '',
                'postalCode': cliente.postalCode or '',
                'observations': cliente.observations or '',
            }
            
            result = asaas_service.create_customer(customer_data)
            
            if result.get('success'):
                cliente.asaas_id = result['data']['id']
                cliente.synced_with_asaas = True
                messages.success(request, 'Cliente cadastrado com sucesso no Asaas!')
            else:
                messages.warning(request, f'Cliente salvo localmente, mas não foi possível sincronizar com Asaas: {result.get("error")}')
            
            cliente.save()
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/form.html', {'form': form, 'title': 'Novo Cliente'})


@login_required(login_url='login')
def cliente_edit(request, pk):
    """Edita um cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            
            # Se já está sincronizado, atualiza no Asaas
            if cliente.asaas_id:
                asaas_service = AsaasService()
                customer_data = {
                    'name': cliente.name,
                    'cpfCnpj': cliente.cpfCnpj,
                    'email': cliente.email,
                    'phone': cliente.phone or '',
                    'mobilePhone': cliente.mobilePhone or '',
                    'address': cliente.address or '',
                    'addressNumber': cliente.addressNumber or '',
                    'complement': cliente.complement or '',
                    'province': cliente.province or '',
                    'postalCode': cliente.postalCode or '',
                    'observations': cliente.observations or '',
                }
                
                result = asaas_service.update_customer(cliente.asaas_id, customer_data)
                
                if result.get('success'):
                    messages.success(request, 'Cliente atualizado com sucesso!')
                else:
                    messages.warning(request, f'Cliente atualizado localmente, mas não foi possível sincronizar com Asaas: {result.get("error")}')
            
            cliente.save()
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'clientes/form.html', {'form': form, 'title': 'Editar Cliente', 'cliente': cliente})


@login_required(login_url='login')
def cliente_delete(request, pk):
    """Deleta um cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        # Se está sincronizado, tenta deletar no Asaas
        if cliente.asaas_id:
            asaas_service = AsaasService()
            result = asaas_service.delete_customer(cliente.asaas_id)
            
            if not result.get('success'):
                messages.warning(request, f'Cliente removido localmente, mas não foi possível remover do Asaas: {result.get("error")}')
        
        cliente.delete()
        messages.success(request, 'Cliente removido com sucesso!')
        return redirect('cliente_list')
    
    return render(request, 'clientes/delete.html', {'cliente': cliente})


@login_required(login_url='login')
def cliente_sync(request, pk):
    """Sincroniza um cliente com o Asaas"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    asaas_service = AsaasService()
    customer_data = {
        'name': cliente.name,
        'cpfCnpj': cliente.cpfCnpj,
        'email': cliente.email,
        'phone': cliente.phone or '',
        'mobilePhone': cliente.mobilePhone or '',
        'address': cliente.address or '',
        'addressNumber': cliente.addressNumber or '',
        'complement': cliente.complement or '',
        'province': cliente.province or '',
        'postalCode': cliente.postalCode or '',
        'observations': cliente.observations or '',
    }
    
    if cliente.asaas_id:
        # Atualiza
        result = asaas_service.update_customer(cliente.asaas_id, customer_data)
    else:
        # Cria
        result = asaas_service.create_customer(customer_data)
        if result.get('success'):
            cliente.asaas_id = result['data']['id']
    
    if result.get('success'):
        cliente.synced_with_asaas = True
        cliente.save()
        messages.success(request, 'Cliente sincronizado com sucesso!')
    else:
        messages.error(request, f'Erro ao sincronizar cliente: {result.get("error")}')
    
    return redirect('cliente_list')


# ==================== RECORRÊNCIAS ====================

@login_required(login_url='login')
def recorrencia_list(request):
    """Lista todas as recorrências com filtros e pesquisa"""
    recorrencias = Recorrencia.objects.select_related('cliente').all()
    
    # Pesquisa por nome do cliente ou descrição
    search_query = request.GET.get('search', '').strip()
    if search_query:
        recorrencias = recorrencias.filter(
            Q(cliente__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filtro por status
    status_filter = request.GET.get('status', '')
    if status_filter:
        recorrencias = recorrencias.filter(status=status_filter)
    
    # Filtro por ciclo
    cycle_filter = request.GET.get('cycle', '')
    if cycle_filter:
        recorrencias = recorrencias.filter(cycle=cycle_filter)
    
    # Filtro por forma de pagamento
    billing_type_filter = request.GET.get('billing_type', '')
    if billing_type_filter:
        recorrencias = recorrencias.filter(billing_type=billing_type_filter)
    
    # Filtro por sincronização
    sync_status = request.GET.get('sync_status', '')
    if sync_status == 'synced':
        recorrencias = recorrencias.filter(synced_with_asaas=True)
    elif sync_status == 'not_synced':
        recorrencias = recorrencias.filter(synced_with_asaas=False)
    
    # Ordenação
    recorrencias = recorrencias.order_by('-created_at')
    
    context = {
        'recorrencias': recorrencias,
        'search_query': search_query,
        'status_filter': status_filter,
        'cycle_filter': cycle_filter,
        'billing_type_filter': billing_type_filter,
        'sync_status': sync_status,
    }
    return render(request, 'recorrencias/list.html', context)


@login_required(login_url='login')
def recorrencia_create(request):
    """Cria uma nova recorrência"""
    if request.method == 'POST':
        form = RecorrenciaForm(request.POST)
        if form.is_valid():
            recorrencia = form.save(commit=False)
            
            # Verifica se o cliente tem asaas_id
            if not recorrencia.cliente.asaas_id:
                messages.error(request, 'O cliente precisa estar sincronizado com o Asaas antes de criar uma recorrência.')
                return render(request, 'recorrencias/form.html', {'form': form, 'title': 'Nova Recorrência'})
            
            # Tenta criar a assinatura no Asaas
            asaas_service = AsaasService()
            subscription_data = {
                'customer': recorrencia.cliente.asaas_id,
                'billingType': recorrencia.billing_type,
                'value': float(recorrencia.value),
                'nextDueDate': recorrencia.next_due_date.strftime('%Y-%m-%d'),
                'cycle': recorrencia.cycle,
                'description': recorrencia.description,
            }
            
            if recorrencia.end_date:
                subscription_data['endDate'] = recorrencia.end_date.strftime('%Y-%m-%d')
            
            if recorrencia.max_payments:
                subscription_data['maxPayments'] = recorrencia.max_payments
            
            result = asaas_service.create_subscription(subscription_data)
            
            if result.get('success'):
                recorrencia.asaas_id = result['data']['id']
                recorrencia.synced_with_asaas = True
                messages.success(request, 'Recorrência cadastrada com sucesso no Asaas!')
            else:
                messages.warning(request, f'Recorrência salva localmente, mas não foi possível sincronizar com Asaas: {result.get("error")}')
            
            recorrencia.save()
            return redirect('recorrencia_list')
    else:
        form = RecorrenciaForm()
    
    return render(request, 'recorrencias/form.html', {'form': form, 'title': 'Nova Recorrência'})


@login_required(login_url='login')
def recorrencia_edit(request, pk):
    """Edita uma recorrência existente"""
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if request.method == 'POST':
        form = RecorrenciaForm(request.POST, instance=recorrencia)
        if form.is_valid():
            recorrencia = form.save(commit=False)
            
            # Se já está sincronizado, atualiza no Asaas
            if recorrencia.asaas_id:
                asaas_service = AsaasService()
                subscription_data = {
                    'billingType': recorrencia.billing_type,
                    'value': float(recorrencia.value),
                    'nextDueDate': recorrencia.next_due_date.strftime('%Y-%m-%d'),
                    'description': recorrencia.description,
                }
                
                if recorrencia.end_date:
                    subscription_data['endDate'] = recorrencia.end_date.strftime('%Y-%m-%d')
                
                result = asaas_service.update_subscription(recorrencia.asaas_id, subscription_data)
                
                if result.get('success'):
                    messages.success(request, 'Recorrência atualizada com sucesso!')
                else:
                    messages.warning(request, f'Recorrência atualizada localmente, mas não foi possível sincronizar com Asaas: {result.get("error")}')
            
            recorrencia.save()
            return redirect('recorrencia_list')
    else:
        form = RecorrenciaForm(instance=recorrencia)
    
    return render(request, 'recorrencias/form.html', {'form': form, 'title': 'Editar Recorrência', 'recorrencia': recorrencia})


@login_required(login_url='login')
def recorrencia_delete(request, pk):
    """Deleta uma recorrência"""
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if request.method == 'POST':
        # Se está sincronizado, tenta deletar no Asaas
        if recorrencia.asaas_id:
            asaas_service = AsaasService()
            result = asaas_service.delete_subscription(recorrencia.asaas_id)
            
            if not result.get('success'):
                messages.warning(request, f'Recorrência removida localmente, mas não foi possível remover do Asaas: {result.get("error")}')
        
        recorrencia.delete()
        messages.success(request, 'Recorrência removida com sucesso!')
        return redirect('recorrencia_list')
    
    return render(request, 'recorrencias/delete.html', {'recorrencia': recorrencia})


@login_required(login_url='login')
def recorrencia_sync(request, pk):
    """Sincroniza uma recorrência com o Asaas"""
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if not recorrencia.cliente.asaas_id:
        messages.error(request, 'O cliente precisa estar sincronizado com o Asaas primeiro.')
        return redirect('recorrencia_list')
    
    asaas_service = AsaasService()
    subscription_data = {
        'customer': recorrencia.cliente.asaas_id,
        'billingType': recorrencia.billing_type,
        'value': float(recorrencia.value),
        'nextDueDate': recorrencia.next_due_date.strftime('%Y-%m-%d'),
        'cycle': recorrencia.cycle,
        'description': recorrencia.description,
    }
    
    if recorrencia.end_date:
        subscription_data['endDate'] = recorrencia.end_date.strftime('%Y-%m-%d')
    
    if recorrencia.max_payments:
        subscription_data['maxPayments'] = recorrencia.max_payments
    
    if recorrencia.asaas_id:
        # Atualiza
        result = asaas_service.update_subscription(recorrencia.asaas_id, subscription_data)
    else:
        # Cria
        result = asaas_service.create_subscription(subscription_data)
        if result.get('success'):
            recorrencia.asaas_id = result['data']['id']
    
    if result.get('success'):
        recorrencia.synced_with_asaas = True
        recorrencia.save()
        messages.success(request, 'Recorrência sincronizada com sucesso!')
    else:
        messages.error(request, f'Erro ao sincronizar recorrência: {result.get("error")}')
    
    return redirect('recorrencia_list')


# ==================== IMPORTAÇÃO ====================

@login_required(login_url='login')
def import_clientes(request):
    """Importa clientes do Asaas"""
    if request.method == 'POST':
        asaas_service = AsaasService()
        result = asaas_service.list_customers(limit=100)
        
        if not result.get('success'):
            messages.error(request, f'Erro ao buscar clientes do Asaas: {result.get("error")}')
            return redirect('cliente_list')
        
        clientes_data = result['data'].get('data', [])
        importados = 0
        atualizados = 0
        erros = 0
        
        for customer_data in clientes_data:
            try:
                # Verifica se já existe pelo asaas_id
                cliente, created = Cliente.objects.update_or_create(
                    asaas_id=customer_data['id'],
                    defaults={
                        'name': customer_data.get('name', ''),
                        'cpfCnpj': customer_data.get('cpfCnpj', ''),
                        'email': customer_data.get('email', ''),
                        'phone': customer_data.get('phone', ''),
                        'mobilePhone': customer_data.get('mobilePhone', ''),
                        'address': customer_data.get('address', ''),
                        'addressNumber': customer_data.get('addressNumber', ''),
                        'complement': customer_data.get('complement', ''),
                        'province': customer_data.get('province', ''),
                        'postalCode': customer_data.get('postalCode', ''),
                        'observations': customer_data.get('observations', ''),
                        'synced_with_asaas': True,
                    }
                )
                
                if created:
                    importados += 1
                else:
                    atualizados += 1
                    
            except Exception as e:
                logger.error(f'Erro ao importar cliente {customer_data.get("id")}: {str(e)}')
                erros += 1
        
        if importados > 0:
            messages.success(request, f'{importados} cliente(s) importado(s) com sucesso!')
        if atualizados > 0:
            messages.info(request, f'{atualizados} cliente(s) atualizado(s).')
        if erros > 0:
            messages.warning(request, f'{erros} erro(s) durante a importação.')
        
        return redirect('cliente_list')
    
    return render(request, 'clientes/import.html')


@login_required(login_url='login')
def import_recorrencias(request):
    """Importa recorrências do Asaas"""
    if request.method == 'POST':
        asaas_service = AsaasService()
        result = asaas_service.list_subscriptions(limit=100)
        
        if not result.get('success'):
            messages.error(request, f'Erro ao buscar recorrências do Asaas: {result.get("error")}')
            return redirect('recorrencia_list')
        
        subscriptions_data = result['data'].get('data', [])
        importadas = 0
        atualizadas = 0
        erros = 0
        sem_cliente = 0
        
        for subscription_data in subscriptions_data:
            try:
                # Busca o cliente pelo asaas_id
                customer_id = subscription_data.get('customer')
                if not customer_id:
                    sem_cliente += 1
                    continue
                
                try:
                    cliente = Cliente.objects.get(asaas_id=customer_id)
                except Cliente.DoesNotExist:
                    # Tenta importar o cliente primeiro
                    customer_result = asaas_service.get_customer(customer_id)
                    if customer_result.get('success'):
                        customer_data = customer_result['data']
                        cliente = Cliente.objects.create(
                            asaas_id=customer_data['id'],
                            name=customer_data.get('name', ''),
                            cpfCnpj=customer_data.get('cpfCnpj', ''),
                            email=customer_data.get('email', ''),
                            phone=customer_data.get('phone', ''),
                            mobilePhone=customer_data.get('mobilePhone', ''),
                            address=customer_data.get('address', ''),
                            addressNumber=customer_data.get('addressNumber', ''),
                            complement=customer_data.get('complement', ''),
                            province=customer_data.get('province', ''),
                            postalCode=customer_data.get('postalCode', ''),
                            observations=customer_data.get('observations', ''),
                            synced_with_asaas=True,
                        )
                    else:
                        sem_cliente += 1
                        continue
                
                # Converte a data
                from datetime import datetime
                next_due_date = datetime.strptime(subscription_data.get('nextDueDate'), '%Y-%m-%d').date()
                
                end_date = None
                if subscription_data.get('endDate'):
                    end_date = datetime.strptime(subscription_data.get('endDate'), '%Y-%m-%d').date()
                
                # Verifica se já existe pelo asaas_id
                recorrencia, created = Recorrencia.objects.update_or_create(
                    asaas_id=subscription_data['id'],
                    defaults={
                        'cliente': cliente,
                        'value': subscription_data.get('value', 0),
                        'cycle': subscription_data.get('cycle', 'MONTHLY'),
                        'billing_type': subscription_data.get('billingType', 'BOLETO'),
                        'description': subscription_data.get('description', 'Importado do Asaas'),
                        'next_due_date': next_due_date,
                        'end_date': end_date,
                        'max_payments': subscription_data.get('maxPayments'),
                        'status': subscription_data.get('status', 'ACTIVE'),
                        'synced_with_asaas': True,
                    }
                )
                
                if created:
                    importadas += 1
                else:
                    atualizadas += 1
                    
            except Exception as e:
                logger.error(f'Erro ao importar recorrência {subscription_data.get("id")}: {str(e)}')
                erros += 1
        
        if importadas > 0:
            messages.success(request, f'{importadas} recorrência(s) importada(s) com sucesso!')
        if atualizadas > 0:
            messages.info(request, f'{atualizadas} recorrência(s) atualizada(s).')
        if sem_cliente > 0:
            messages.warning(request, f'{sem_cliente} recorrência(s) não importadas (cliente não encontrado).')
        if erros > 0:
            messages.warning(request, f'{erros} erro(s) durante a importação.')
        
        return redirect('recorrencia_list')
    
    return render(request, 'recorrencias/import.html')


# ==================== PLANO DE CONTAS ====================

@login_required(login_url='login')
def plano_contas_list(request):
    """Lista o plano de contas"""
    categorias = PlanoContas.objects.filter(ativa=True).select_related('categoria_pai')
    
    # Filtros
    tipo = request.GET.get('tipo', '')
    if tipo:
        categorias = categorias.filter(tipo=tipo)
    
    context = {
        'categorias': categorias,
        'tipo': tipo,
    }
    return render(request, 'financeiro/plano_contas_list.html', context)


@login_required(login_url='login')
def plano_contas_create(request):
    """Cria uma nova categoria"""
    if request.method == 'POST':
        form = PlanoContasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('plano_contas_list')
    else:
        form = PlanoContasForm()
    
    return render(request, 'financeiro/plano_contas_form.html', {'form': form, 'title': 'Nova Categoria'})


@login_required(login_url='login')
def plano_contas_edit(request, pk):
    """Edita uma categoria"""
    categoria = get_object_or_404(PlanoContas, pk=pk)
    
    if request.method == 'POST':
        form = PlanoContasForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('plano_contas_list')
    else:
        form = PlanoContasForm(instance=categoria)
    
    return render(request, 'financeiro/plano_contas_form.html', {'form': form, 'title': 'Editar Categoria', 'categoria': categoria})


@login_required(login_url='login')
def plano_contas_delete(request, pk):
    """Deleta uma categoria"""
    categoria = get_object_or_404(PlanoContas, pk=pk)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria removida com sucesso!')
        return redirect('plano_contas_list')
    
    return render(request, 'financeiro/plano_contas_delete.html', {'categoria': categoria})


# ==================== MOVIMENTAÇÕES ====================

@login_required(login_url='login')
def movimentacao_list(request):
    """Lista movimentações com filtros"""
    movimentacoes = Movimentacao.objects.select_related('cliente', 'plano_contas').all()
    
    # Filtros
    search_query = request.GET.get('search', '').strip()
    if search_query:
        movimentacoes = movimentacoes.filter(
            Q(descricao__icontains=search_query) |
            Q(cliente__name__icontains=search_query)
        )
    
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    if data_inicio:
        movimentacoes = movimentacoes.filter(data__gte=data_inicio)
    if data_fim:
        movimentacoes = movimentacoes.filter(data__lte=data_fim)
    
    tipo = request.GET.get('tipo', '')
    if tipo:
        movimentacoes = movimentacoes.filter(tipo=tipo)
    
    status_conciliacao = request.GET.get('status_conciliacao', '')
    if status_conciliacao:
        movimentacoes = movimentacoes.filter(status_conciliacao=status_conciliacao)
    
    categoria = request.GET.get('categoria', '')
    if categoria:
        movimentacoes = movimentacoes.filter(plano_contas_id=categoria)
    
    # Estatísticas
    total_receitas = movimentacoes.filter(valor__gt=0).aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = movimentacoes.filter(valor__lt=0).aggregate(Sum('valor'))['valor__sum'] or 0
    nao_conciliadas = movimentacoes.filter(status_conciliacao='NAO_CONCILIADO').count()
    
    context = {
        'movimentacoes': movimentacoes.order_by('-data'),
        'search_query': search_query,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo': tipo,
        'status_conciliacao': status_conciliacao,
        'categoria': categoria,
        'total_receitas': total_receitas,
        'total_despesas': abs(total_despesas),
        'saldo': total_receitas + total_despesas,
        'nao_conciliadas': nao_conciliadas,
        'categorias': PlanoContas.objects.filter(ativa=True),
    }
    return render(request, 'financeiro/movimentacao_list.html', context)


@login_required(login_url='login')
def movimentacao_edit(request, pk):
    """Edita/concilia uma movimentação"""
    movimentacao = get_object_or_404(Movimentacao, pk=pk)
    
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, instance=movimentacao)
        if form.is_valid():
            mov = form.save(commit=False)
            # Se foi categorizada manualmente
            if mov.plano_contas and mov.status_conciliacao == 'NAO_CONCILIADO':
                mov.status_conciliacao = 'CONCILIADO_MANUAL'
            mov.save()
            messages.success(request, 'Movimentação atualizada com sucesso!')
            return redirect('movimentacao_list')
    else:
        form = MovimentacaoForm(instance=movimentacao)
    
    return render(request, 'financeiro/movimentacao_form.html', {'form': form, 'movimentacao': movimentacao})


@login_required(login_url='login')
def movimentacao_delete(request, pk):
    """Deleta uma movimentação"""
    movimentacao = get_object_or_404(Movimentacao, pk=pk)
    
    if request.method == 'POST':
        movimentacao.delete()
        messages.success(request, 'Movimentação removida com sucesso!')
        return redirect('movimentacao_list')
    
    return render(request, 'financeiro/movimentacao_delete.html', {'movimentacao': movimentacao})


@login_required(login_url='login')
def import_movimentacoes(request):
    """Importa movimentações do Asaas"""
    if request.method == 'POST':
        # Pega parâmetros de data
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        
        if not data_inicio or not data_fim:
            messages.error(request, 'Por favor, informe o período para importação.')
            return render(request, 'financeiro/import_movimentacoes.html')
        
        asaas_service = AsaasService()
        importadas = 0
        atualizadas = 0
        erros = 0
        
        # Busca transações financeiras
        result = asaas_service.get_financial_transactions(
            limit=500, 
            date_from=data_inicio, 
            date_to=data_fim
        )
        
        if not result.get('success'):
            messages.error(request, f'Erro ao buscar movimentações: {result.get("error")}')
            return redirect('movimentacao_list')
        
        transactions = result['data'].get('data', [])
        
        for trans in transactions:
            try:
                # Mapeia o tipo de transação
                tipo_map = {
                    'PAYMENT': 'PAYMENT',
                    'PAYMENT_FEE': 'PAYMENT_FEE',
                    'TRANSFER': 'TRANSFER',
                    'TRANSFER_FEE': 'TRANSFER_FEE',
                    'REFUND': 'REFUND',
                    'CHARGEBACK': 'CHARGEBACK',
                }
                tipo = tipo_map.get(trans.get('type'), 'OTHER')
                
                # Tenta encontrar cliente relacionado
                cliente = None
                if trans.get('customer'):
                    try:
                        cliente = Cliente.objects.get(asaas_id=trans['customer'])
                    except Cliente.DoesNotExist:
                        pass
                
                # Cria ou atualiza movimentação
                movimentacao, created = Movimentacao.objects.update_or_create(
                    asaas_id=trans['id'],
                    defaults={
                        'data': datetime.strptime(trans['date'], '%Y-%m-%d').date(),
                        'descricao': trans.get('description', ''),
                        'tipo': tipo,
                        'valor': trans.get('value', 0),
                        'cliente': cliente,
                        'dados_asaas': trans,
                        'synced_with_asaas': True,
                    }
                )
                
                if created:
                    importadas += 1
                    # Tenta aplicar regras de categorização automática
                    aplicar_regras_categorizacao(movimentacao)
                else:
                    atualizadas += 1
                    
            except Exception as e:
                logger.error(f'Erro ao importar movimentação {trans.get("id")}: {str(e)}')
                erros += 1
        
        if importadas > 0:
            messages.success(request, f'{importadas} movimentação(ões) importada(s) com sucesso!')
        if atualizadas > 0:
            messages.info(request, f'{atualizadas} movimentação(ões) atualizada(s).')
        if erros > 0:
            messages.warning(request, f'{erros} erro(s) durante a importação.')
        
        return redirect('movimentacao_list')
    
    return render(request, 'financeiro/import_movimentacoes.html')


# ==================== REGRAS DE CATEGORIZAÇÃO ====================

@login_required(login_url='login')
def regra_list(request):
    """Lista regras de categorização"""
    regras = RegraCategorizacao.objects.select_related('plano_contas').all()
    
    context = {
        'regras': regras,
    }
    return render(request, 'financeiro/regra_list.html', context)


@login_required(login_url='login')
def regra_create(request):
    """Cria uma nova regra"""
    if request.method == 'POST':
        form = RegraCategorizacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Regra criada com sucesso!')
            return redirect('regra_list')
    else:
        form = RegraCategorizacaoForm()
    
    return render(request, 'financeiro/regra_form.html', {'form': form, 'title': 'Nova Regra'})


@login_required(login_url='login')
def regra_edit(request, pk):
    """Edita uma regra"""
    regra = get_object_or_404(RegraCategorizacao, pk=pk)
    
    if request.method == 'POST':
        form = RegraCategorizacaoForm(request.POST, instance=regra)
        if form.is_valid():
            form.save()
            messages.success(request, 'Regra atualizada com sucesso!')
            return redirect('regra_list')
    else:
        form = RegraCategorizacaoForm(instance=regra)
    
    return render(request, 'financeiro/regra_form.html', {'form': form, 'title': 'Editar Regra', 'regra': regra})


@login_required(login_url='login')
def regra_delete(request, pk):
    """Deleta uma regra"""
    regra = get_object_or_404(RegraCategorizacao, pk=pk)
    
    if request.method == 'POST':
        regra.delete()
        messages.success(request, 'Regra removida com sucesso!')
        return redirect('regra_list')
    
    return render(request, 'financeiro/regra_delete.html', {'regra': regra})


@login_required(login_url='login')
def aplicar_regras_manual(request):
    """Aplica regras de categorização em movimentações não conciliadas"""
    movimentacoes = Movimentacao.objects.filter(status_conciliacao='NAO_CONCILIADO')
    categorizadas = 0
    
    for mov in movimentacoes:
        if aplicar_regras_categorizacao(mov):
            categorizadas += 1
    
    messages.success(request, f'{categorizadas} movimentação(ões) categorizada(s) automaticamente!')
    return redirect('movimentacao_list')


def aplicar_regras_categorizacao(movimentacao):
    """
    Aplica regras de categorização automática em uma movimentação
    Retorna True se alguma regra foi aplicada
    """
    if movimentacao.status_conciliacao != 'NAO_CONCILIADO':
        return False
    
    regras = RegraCategorizacao.objects.filter(ativa=True).order_by('-prioridade', 'id')
    
    for regra in regras:
        if regra.aplicar(movimentacao):
            movimentacao.plano_contas = regra.plano_contas
            movimentacao.status_conciliacao = 'CONCILIADO_AUTO'
            movimentacao.save()
            
            regra.vezes_aplicada += 1
            regra.save(update_fields=['vezes_aplicada'])
            
            return True
    
    return False


# ==================== CONCILIAÇÃO ====================

@login_required(login_url='login')
def conciliacao(request):
    """Interface de conciliação manual"""
    movimentacoes = Movimentacao.objects.filter(
        status_conciliacao='NAO_CONCILIADO'
    ).select_related('cliente').order_by('-data')
    
    categorias = PlanoContas.objects.filter(ativa=True)
    
    context = {
        'movimentacoes': movimentacoes,
        'categorias': categorias,
        'total': movimentacoes.count(),
    }
    return render(request, 'financeiro/conciliacao.html', context)


@login_required(login_url='login')
def conciliar_rapido(request, pk):
    """Concilia rapidamente uma movimentação via AJAX"""
    if request.method == 'POST':
        movimentacao = get_object_or_404(Movimentacao, pk=pk)
        categoria_id = request.POST.get('categoria_id')
        
        if categoria_id:
            categoria = get_object_or_404(PlanoContas, pk=categoria_id)
            movimentacao.plano_contas = categoria
            movimentacao.status_conciliacao = 'CONCILIADO_MANUAL'
            movimentacao.save()
            
            return JsonResponse({'success': True, 'message': 'Conciliado com sucesso!'})
        
        return JsonResponse({'success': False, 'message': 'Categoria não informada'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


# ==================== RELATÓRIOS ====================

@login_required(login_url='login')
def relatorios(request):
    """Dashboard de relatórios financeiros"""
    # Período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if not data_inicio:
        data_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not data_fim:
        data_fim = datetime.now().strftime('%Y-%m-%d')
    
    movimentacoes = Movimentacao.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim
    )
    
    # Totais
    total_receitas = movimentacoes.filter(valor__gt=0).aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = movimentacoes.filter(valor__lt=0).aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_receitas + total_despesas
    
    # Por categoria
    por_categoria = movimentacoes.filter(
        plano_contas__isnull=False
    ).values(
        'plano_contas__nome',
        'plano_contas__tipo'
    ).annotate(
        total=Sum('valor'),
        quantidade=Count('id')
    ).order_by('-total')
    
    # Por mês
    por_mes = movimentacoes.annotate(
        mes=TruncMonth('data')
    ).values('mes').annotate(
        receitas=Sum('valor', filter=Q(valor__gt=0)),
        despesas=Sum('valor', filter=Q(valor__lt=0)),
    ).order_by('mes')
    
    # Status de conciliação
    conciliacao_stats = {
        'nao_conciliado': movimentacoes.filter(status_conciliacao='NAO_CONCILIADO').count(),
        'conciliado_auto': movimentacoes.filter(status_conciliacao='CONCILIADO_AUTO').count(),
        'conciliado_manual': movimentacoes.filter(status_conciliacao='CONCILIADO_MANUAL').count(),
    }
    
    # Top clientes
    top_clientes = movimentacoes.filter(
        cliente__isnull=False,
        valor__gt=0
    ).values(
        'cliente__name'
    ).annotate(
        total=Sum('valor'),
        quantidade=Count('id')
    ).order_by('-total')[:10]
    
    context = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_receitas': total_receitas,
        'total_despesas': abs(total_despesas),
        'saldo': saldo,
        'por_categoria': por_categoria,
        'por_mes': por_mes,
        'conciliacao_stats': conciliacao_stats,
        'top_clientes': top_clientes,
    }
    return render(request, 'financeiro/relatorios.html', context)
