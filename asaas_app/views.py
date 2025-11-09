from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from .models import Cliente, Recorrencia, PlanoContas, Movimentacao, RegraCategorizacao, LinkPagamento
from .forms import ClienteForm, RecorrenciaForm, PlanoContasForm, MovimentacaoForm, RegraCategorizacaoForm, LinkPagamentoForm
from .services import AsaasService
from .whatsapp_service import WhatsAppService
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# ==================== AUTENTICAÇÃO ====================

def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Obter o next_url do GET, se existir
            next_url = request.GET.get('next')
            
            # Determinar URL de destino
            if next_url and not next_url.startswith('http'):
                redirect_url = next_url
            else:
                redirect_url = reverse('home')
            
            # Log para debug
            logger.info(f"Login successful for {user.username}, redirecting to: {redirect_url}")
            
            # Adicionar mensagem apenas após determinar o redirect
            messages.success(request, f'Bem-vindo, {user.username}!')
            
            return redirect(redirect_url)
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
    try:
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
    except Exception as e:
        logger.error(f"Erro ao listar recorrências: {str(e)}", exc_info=True)
        messages.error(request, f'Erro ao carregar recorrências: {str(e)}')
        return render(request, 'recorrencias/list.html', {'recorrencias': []})


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
                
                # Cria link de pagamento automaticamente
                criar_link_pagamento_recorrencia(recorrencia)
                
                # Envia mensagem WhatsApp para o cliente
                enviar_whatsapp_recorrencia(recorrencia)
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
def recorrencia_boletos(request, pk):
    """
    Lista os boletos (cobranças) de uma recorrência e permite download
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if not recorrencia.asaas_id:
        messages.error(request, 'Esta recorrência precisa estar sincronizada com o Asaas para visualizar os boletos.')
        return redirect('recorrencia_list')
    
    # Busca as cobranças da assinatura no Asaas
    asaas_service = AsaasService()
    result = asaas_service.list_subscription_payments(recorrencia.asaas_id)
    
    boletos = []
    if result.get('success'):
        payments = result['data'].get('data', [])
        for payment in payments:
            boletos.append({
                'id': payment.get('id'),
                'value': payment.get('value'),
                'dueDate': payment.get('dueDate'),
                'status': payment.get('status'),
                'bankSlipUrl': payment.get('bankSlipUrl'),
                'invoiceUrl': payment.get('invoiceUrl'),
                'billingType': payment.get('billingType'),
            })
    else:
        messages.error(request, f'Erro ao buscar boletos: {result.get("error")}')
    
    context = {
        'recorrencia': recorrencia,
        'boletos': boletos,
    }
    
    return render(request, 'recorrencias/boletos.html', context)


@login_required(login_url='login')
def recorrencia_enviar_boleto_whatsapp(request, pk):
    """
    Busca o último boleto da recorrência e envia pelo WhatsApp
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    # Verifica se tem telefone
    telefone = recorrencia.cliente.mobilePhone or recorrencia.cliente.phone
    if not telefone:
        messages.error(request, 'Cliente não possui telefone cadastrado.')
        return redirect('recorrencia_list')
    
    # Verifica se está sincronizada
    if not recorrencia.asaas_id:
        messages.error(request, 'Recorrência precisa estar sincronizada com o Asaas.')
        return redirect('recorrencia_list')
    
    # Busca o último boleto
    asaas_service = AsaasService()
    result = asaas_service.list_subscription_payments(recorrencia.asaas_id, limit=1)
    
    if not result.get('success') or not result['data'].get('data'):
        messages.error(request, 'Nenhum boleto encontrado para esta recorrência.')
        return redirect('recorrencia_list')
    
    boleto = result['data']['data'][0]
    bank_slip_url = boleto.get('bankSlipUrl')
    
    if not bank_slip_url:
        messages.error(request, 'Boleto não possui URL de download.')
        return redirect('recorrencia_list')
    
    # Formata a mensagem
    cliente_nome = recorrencia.cliente.name.split()[0]  # Primeiro nome
    valor = boleto.get('value', recorrencia.value)
    vencimento = boleto.get('dueDate', recorrencia.next_due_date)
    
    mensagem = f"""Olá *{cliente_nome}*! 👋

🔔 *Cobrança Recorrente - {recorrencia.description}*

💰 Valor: R$ {valor}
📅 Vencimento: {vencimento}

📄 *Acesse seu boleto:*
{bank_slip_url}

Você também pode pagar via PIX usando o QR Code que está no boleto.

✅ Após o pagamento, você receberá a confirmação automaticamente.

Dúvidas? Estamos à disposição!

Atenciosamente,
Equipe de Cobrança"""
    
    # Envia pelo WhatsApp
    whatsapp_service = WhatsAppService()
    result_whatsapp = whatsapp_service.send_message(telefone, mensagem)
    
    if result_whatsapp.get('success'):
        messages.success(request, f'Boleto enviado com sucesso para {telefone}!')
    else:
        messages.error(request, f'Erro ao enviar WhatsApp: {result_whatsapp.get("error")}')
    
    return redirect('recorrencia_list')


@login_required(login_url='login')
def recorrencia_enviar_link_whatsapp(request, pk):
    """
    Envia link de pagamento da recorrência pelo WhatsApp
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    # Verifica se tem telefone
    telefone = recorrencia.cliente.mobilePhone or recorrencia.cliente.phone
    if not telefone:
        messages.error(request, 'Cliente não possui telefone cadastrado.')
        return redirect('recorrencia_list')
    
    # Busca o link de pagamento desta recorrência
    link = LinkPagamento.objects.filter(
        cliente=recorrencia.cliente,
        nome__icontains=recorrencia.description
    ).first()
    
    if not link or not link.url:
        messages.error(request, 'Nenhum link de pagamento encontrado. Crie um link primeiro.')
        return redirect('recorrencia_list')
    
    # Formata a mensagem
    cliente_nome = recorrencia.cliente.name.split()[0]  # Primeiro nome
    
    mensagem = f"""Olá *{cliente_nome}*! 👋

🔗 *Link de Pagamento - {recorrencia.description}*

💰 Valor: R$ {recorrencia.value}
🔄 Frequência: {recorrencia.get_cycle_display()}

📲 *Clique no link abaixo para pagar:*
{link.url}

✅ Escolha sua forma de pagamento preferida:
• PIX (instantâneo)
• Boleto Bancário
• Cartão de Crédito

Após o pagamento, você receberá a confirmação automaticamente.

Dúvidas? Estamos à disposição!

Atenciosamente,
Equipe de Cobrança"""
    
    # Envia pelo WhatsApp
    whatsapp_service = WhatsAppService()
    result_whatsapp = whatsapp_service.send_message(telefone, mensagem)
    
    if result_whatsapp.get('success'):
        messages.success(request, f'Link de pagamento enviado com sucesso para {telefone}!')
    else:
        messages.error(request, f'Erro ao enviar WhatsApp: {result_whatsapp.get("error")}')
    
    return redirect('recorrencia_list')


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
        total_liquido_periodo = Decimal('0')

        # Paginação: busca todas as páginas do período informado
        limit = 500
        offset = 0
        while True:
            result = asaas_service.get_financial_transactions(
                limit=limit,
                offset=offset,
                date_from=data_inicio,
                date_to=data_fim
            )

            if not result.get('success'):
                messages.error(request, f'Erro ao buscar movimentações: {result.get("error")}')
                break

            transactions = result['data'].get('data', [])

            if not transactions:
                break

            for trans in transactions:
                try:
                    # Soma líquida do período (usa o valor retornado pela API)
                    try:
                        total_liquido_periodo += Decimal(str(trans.get('value', 0)))
                    except Exception:
                        pass

                    # Mapeia o tipo de transação
                    tipo_map = {
                        'PAYMENT': 'PAYMENT',
                        'PAYMENT_FEE': 'PAYMENT_FEE',
                        'TRANSFER': 'TRANSFER',
                        'TRANSFER_FEE': 'TRANSFER_FEE',
                        'REFUND': 'REFUND',
                        'CHARGEBACK': 'CHARGEBACK',
                        'ANTICIPATION': 'ANTICIPATION',
                        'ANTICIPATION_FEE': 'ANTICIPATION_FEE',
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

            # Avança a janela de paginação
            offset += len(transactions)

            # Se a API informar que não há mais páginas, encerra
            has_more = result['data'].get('hasMore')
            if has_more is False or len(transactions) < limit:
                break

        if importadas > 0:
            messages.success(request, f'{importadas} movimentação(ões) importada(s) com sucesso!')
        if atualizadas > 0:
            messages.info(request, f'{atualizadas} movimentação(ões) atualizada(s).')
        if erros > 0:
            messages.warning(request, f'{erros} erro(s) durante a importação.')
        # Resumo do valor líquido do período
        messages.info(request, f"Valor líquido do período importado: {total_liquido_periodo}")

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


# ==================== LINKS DE PAGAMENTO ====================

@login_required(login_url='login')
def link_pagamento_list(request):
    """Lista todos os links de pagamento"""
    links = LinkPagamento.objects.select_related('cliente').all()
    
    # Filtros
    search_query = request.GET.get('search', '').strip()
    if search_query:
        links = links.filter(
            Q(nome__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        links = links.filter(status=status_filter)
    
    charge_type_filter = request.GET.get('charge_type', '')
    if charge_type_filter:
        links = links.filter(charge_type=charge_type_filter)
    
    context = {
        'links': links.order_by('-created_at'),
        'search_query': search_query,
        'status_filter': status_filter,
        'charge_type_filter': charge_type_filter,
    }
    return render(request, 'links_pagamento/list.html', context)


@login_required(login_url='login')
def link_pagamento_create(request):
    """Cria um novo link de pagamento"""
    if request.method == 'POST':
        form = LinkPagamentoForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            
            # Prepara dados para o Asaas
            asaas_service = AsaasService()
            payment_link_data = {
                'name': link.nome,
                'description': link.descricao or '',
                'billingType': link.billing_type,
                'chargeType': link.charge_type,
            }
            
            # Adiciona valor se informado
            if link.valor:
                payment_link_data['value'] = float(link.valor)
            
            # Adiciona prazo de vencimento se informado
            if link.due_date_limit_days:
                payment_link_data['dueDateLimitDays'] = link.due_date_limit_days
            
            # Adiciona máximo de parcelas se informado
            if link.max_installments:
                payment_link_data['maxInstallments'] = link.max_installments
            
            # Adiciona cliente se informado
            if link.cliente and link.cliente.asaas_id:
                payment_link_data['customer'] = link.cliente.asaas_id
            
            # Cria no Asaas
            result = asaas_service.create_payment_link(payment_link_data)
            
            if result.get('success'):
                data = result['data']
                link.asaas_id = data.get('id')
                link.url = data.get('url')
                link.status = data.get('status', 'ACTIVE')
                link.synced_with_asaas = True
                messages.success(request, 'Link de pagamento criado com sucesso no Asaas!')
            else:
                messages.warning(request, f'Link salvo localmente, mas não foi possível criar no Asaas: {result.get("error")}')
            
            link.save()
            return redirect('link_pagamento_list')
    else:
        form = LinkPagamentoForm()
    
    return render(request, 'links_pagamento/form.html', {'form': form, 'title': 'Novo Link de Pagamento'})


@login_required(login_url='login')
def link_pagamento_edit(request, pk):
    """Edita um link de pagamento existente"""
    link = get_object_or_404(LinkPagamento, pk=pk)
    
    if request.method == 'POST':
        form = LinkPagamentoForm(request.POST, instance=link)
        if form.is_valid():
            link = form.save(commit=False)
            
            # Se está sincronizado, atualiza no Asaas
            if link.asaas_id:
                asaas_service = AsaasService()
                payment_link_data = {
                    'name': link.nome,
                    'description': link.descricao or '',
                    'billingType': link.billing_type,
                }
                
                if link.valor:
                    payment_link_data['value'] = float(link.valor)
                
                if link.due_date_limit_days:
                    payment_link_data['dueDateLimitDays'] = link.due_date_limit_days
                
                result = asaas_service.update_payment_link(link.asaas_id, payment_link_data)
                
                if result.get('success'):
                    data = result.get('data', {})
                    link.url = data.get('url', link.url)
                    link.status = data.get('status', link.status)
                    messages.success(request, 'Link de pagamento atualizado com sucesso!')
                else:
                    messages.warning(request, f'Link atualizado localmente, mas não foi possível atualizar no Asaas: {result.get("error")}')
            
            link.save()
            return redirect('link_pagamento_list')
    else:
        form = LinkPagamentoForm(instance=link)
    
    return render(request, 'links_pagamento/form.html', {'form': form, 'title': 'Editar Link de Pagamento', 'link': link})


@login_required(login_url='login')
def link_pagamento_delete(request, pk):
    """Deleta um link de pagamento"""
    link = get_object_or_404(LinkPagamento, pk=pk)
    
    if request.method == 'POST':
        # Se está sincronizado, tenta deletar no Asaas
        if link.asaas_id:
            asaas_service = AsaasService()
            result = asaas_service.delete_payment_link(link.asaas_id)
            
            if not result.get('success'):
                messages.warning(request, f'Link removido localmente, mas não foi possível remover do Asaas: {result.get("error")}')
        
        link.delete()
        messages.success(request, 'Link de pagamento removido com sucesso!')
        return redirect('link_pagamento_list')
    
    return render(request, 'links_pagamento/delete.html', {'link': link})


@login_required(login_url='login')
def link_pagamento_sync(request, pk):
    """Sincroniza um link de pagamento com o Asaas"""
    link = get_object_or_404(LinkPagamento, pk=pk)
    
    if not link.asaas_id:
        messages.error(request, 'Link não possui ID do Asaas. Crie um novo link.')
        return redirect('link_pagamento_list')
    
    asaas_service = AsaasService()
    result = asaas_service.get_payment_link(link.asaas_id)
    
    if result.get('success'):
        data = result['data']
        link.url = data.get('url', link.url)
        link.status = data.get('status', link.status)
        link.nome = data.get('name', link.nome)
        link.descricao = data.get('description', link.descricao)
        if data.get('value'):
            link.valor = data.get('value')
        link.synced_with_asaas = True
        link.save()
        messages.success(request, 'Link de pagamento sincronizado com sucesso!')
    else:
        messages.error(request, f'Erro ao sincronizar link: {result.get("error")}')
    
    return redirect('link_pagamento_list')


@login_required(login_url='login')
def import_link_pagamento(request):
    """Importa links de pagamento do Asaas"""
    if request.method == 'POST':
        asaas_service = AsaasService()
        importados = 0
        atualizados = 0
        erros = 0
        
        # Busca todas as páginas
        limit = 100
        offset = 0
        
        while True:
            result = asaas_service.list_payment_links(limit=limit, offset=offset)
            
            if not result.get('success'):
                messages.error(request, f'Erro ao buscar links: {result.get("error")}')
                break
            
            links_data = result['data'].get('data', [])
            
            if not links_data:
                break
            
            for link_data in links_data:
                try:
                    # Busca cliente se informado
                    cliente = None
                    if link_data.get('customer'):
                        try:
                            cliente = Cliente.objects.get(asaas_id=link_data['customer'])
                        except Cliente.DoesNotExist:
                            pass
                    
                    # Cria ou atualiza link
                    link, created = LinkPagamento.objects.update_or_create(
                        asaas_id=link_data['id'],
                        defaults={
                            'nome': link_data.get('name', ''),
                            'descricao': link_data.get('description', ''),
                            'valor': link_data.get('value'),
                            'billing_type': link_data.get('billingType', 'UNDEFINED'),
                            'charge_type': link_data.get('chargeType', 'DETACHED'),
                            'due_date_limit_days': link_data.get('dueDateLimitDays'),
                            'max_installments': link_data.get('maxInstallments'),
                            'cliente': cliente,
                            'url': link_data.get('url'),
                            'status': link_data.get('status', 'ACTIVE'),
                            'synced_with_asaas': True,
                        }
                    )
                    
                    if created:
                        importados += 1
                    else:
                        atualizados += 1
                        
                except Exception as e:
                    logger.error(f'Erro ao importar link {link_data.get("id")}: {str(e)}')
                    erros += 1
            
            # Avança paginação
            offset += len(links_data)
            
            # Verifica se há mais páginas
            has_more = result['data'].get('hasMore')
            if has_more is False or len(links_data) < limit:
                break
        
        if importados > 0:
            messages.success(request, f'{importados} link(s) importado(s) com sucesso!')
        if atualizados > 0:
            messages.info(request, f'{atualizados} link(s) atualizado(s).')
        if erros > 0:
            messages.warning(request, f'{erros} erro(s) durante a importação.')
        
        return redirect('link_pagamento_list')
    
    # Estatísticas para exibir na página
    links_locais = LinkPagamento.objects.count()
    links_sincronizados = LinkPagamento.objects.filter(synced_with_asaas=True).count()
    links_ativos = LinkPagamento.objects.filter(status='ACTIVE').count()
    
    context = {
        'links_locais': links_locais,
        'links_sincronizados': links_sincronizados,
        'links_ativos': links_ativos,
    }
    
    return render(request, 'links_pagamento/import.html', context)


# ==================== LINK DE PAGAMENTO ====================

@login_required(login_url='login')
def recorrencia_criar_link(request, pk):
    """
    Cria um link de pagamento a partir de uma recorrência existente
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    # Verifica se já existe um link para esta recorrência
    link_existente = LinkPagamento.objects.filter(
        cliente=recorrencia.cliente,
        nome__icontains=recorrencia.description
    ).first()
    
    if link_existente:
        messages.info(request, f'Já existe um link de pagamento para esta recorrência. Redirecionando para a lista de links.')
        return redirect('link_pagamento_list')
    
    # Cria o link de pagamento
    link = criar_link_pagamento_recorrencia(recorrencia)
    
    if link:
        messages.success(request, f'Link de pagamento criado com sucesso! Você pode visualizá-lo e copiar a URL abaixo.')
        return redirect('link_pagamento_list')
    else:
        messages.error(request, 'Erro ao criar link de pagamento. Verifique os logs.')
        return redirect('recorrencia_list')


def criar_link_pagamento_recorrencia(recorrencia):
    """
    Cria automaticamente um link de pagamento quando uma recorrência é criada
    
    Args:
        recorrencia: Objeto Recorrencia
    """
    try:
        # Verifica se já existe um link para esta recorrência
        link_existente = LinkPagamento.objects.filter(
            cliente=recorrencia.cliente,
            nome__icontains=recorrencia.description
        ).first()
        
        if link_existente:
            logger.info(f'Link de pagamento já existe para recorrência {recorrencia.asaas_id}')
            return link_existente
        
        # Prepara dados do link de pagamento
        asaas_service = AsaasService()
        payment_link_data = {
            'name': f"{recorrencia.description} - Recorrência",
            'description': f"Link de pagamento para {recorrencia.description}",
            'billingType': recorrencia.billing_type,
            'chargeType': 'DETACHED',  # Mudado para DETACHED para evitar formulário
            'value': float(recorrencia.value),
            'dueDateLimitDays': 30,  # Prazo de vencimento em dias (obrigatório pela API)
        }
        
        # IMPORTANTE: Adiciona cliente para ir direto ao pagamento sem formulário
        if recorrencia.cliente.asaas_id:
            payment_link_data['customer'] = recorrencia.cliente.asaas_id
        else:
            # Se cliente não tem asaas_id, sincroniza primeiro
            logger.warning(f'Cliente {recorrencia.cliente.name} não tem asaas_id. Tentando sincronizar...')
            customer_data = {
                'name': recorrencia.cliente.name,
                'cpfCnpj': recorrencia.cliente.cpfCnpj,
                'email': recorrencia.cliente.email,
                'mobilePhone': recorrencia.cliente.mobilePhone or recorrencia.cliente.phone,
            }
            customer_result = asaas_service.create_customer(customer_data)
            if customer_result.get('success'):
                recorrencia.cliente.asaas_id = customer_result['data']['id']
                recorrencia.cliente.synced_with_asaas = True
                recorrencia.cliente.save()
                payment_link_data['customer'] = recorrencia.cliente.asaas_id
                logger.info(f'Cliente {recorrencia.cliente.name} sincronizado com sucesso!')
            else:
                logger.error(f'Erro ao sincronizar cliente: {customer_result.get("error")}')
        
        # Cria o link no Asaas
        result = asaas_service.create_payment_link(payment_link_data)
        
        if result.get('success'):
            data = result['data']
            
            # Cria o link no banco local
            link = LinkPagamento.objects.create(
                nome=payment_link_data['name'],
                descricao=payment_link_data['description'],
                valor=recorrencia.value,
                billing_type=recorrencia.billing_type,
                charge_type='DETACHED',  # Mudado para DETACHED
                cliente=recorrencia.cliente,
                due_date_limit_days=payment_link_data.get('dueDateLimitDays', 30),
                asaas_id=data.get('id'),
                url=data.get('url'),
                status=data.get('status', 'ACTIVE'),
                synced_with_asaas=True,
            )
            
            logger.info(f'Link de pagamento criado automaticamente para recorrência {recorrencia.asaas_id}: {link.url}')
            return link
        else:
            logger.error(f'Erro ao criar link de pagamento para recorrência {recorrencia.asaas_id}: {result.get("error")}')
            return None
            
    except Exception as e:
        logger.error(f'Erro ao criar link de pagamento automaticamente: {str(e)}')
        return None


# ==================== WHATSAPP ====================

def enviar_whatsapp_recorrencia(recorrencia):
    """
    Envia mensagem WhatsApp para o cliente quando uma recorrência é criada
    
    Args:
        recorrencia: Objeto Recorrencia
    """
    # Verifica se o cliente tem telefone cadastrado
    cliente = recorrencia.cliente
    telefone = cliente.mobilePhone or cliente.phone
    
    if not telefone:
        logger.warning(f'Cliente {cliente.name} não possui telefone cadastrado para envio de WhatsApp')
        return
    
    # Busca o link de pagamento criado para esta recorrência
    link_pagamento = LinkPagamento.objects.filter(
        cliente=recorrencia.cliente,
        nome__icontains=recorrencia.description
    ).first()
    
    # Formata a mensagem
    ciclo_nome = dict(Recorrencia.CYCLE_CHOICES).get(recorrencia.cycle, recorrencia.cycle)
    forma_pagamento = dict(Recorrencia.BILLING_TYPE_CHOICES).get(recorrencia.billing_type, recorrencia.billing_type)
    
    mensagem = f"""Olá {cliente.name}! 👋

Sua recorrência foi criada com sucesso! ✅

📋 *Detalhes da Recorrência:*
• Descrição: {recorrencia.description}
• Valor: R$ {recorrencia.value:.2f}
• Ciclo: {ciclo_nome}
• Forma de Pagamento: {forma_pagamento}
• Próximo Vencimento: {recorrencia.next_due_date.strftime('%d/%m/%Y')}
"""
    
    if recorrencia.end_date:
        mensagem += f"• Data de Término: {recorrencia.end_date.strftime('%d/%m/%Y')}\n"
    
    if recorrencia.max_payments:
        mensagem += f"• Total de Cobranças: {recorrencia.max_payments}\n"
    
    # Adiciona link de pagamento se disponível
    if link_pagamento and link_pagamento.url:
        mensagem += f"""
🔗 *Link de Pagamento:*
{link_pagamento.url}

💡 *Como usar:*
Clique no link acima para realizar o pagamento da sua recorrência.
"""
    
    mensagem += f"""
📌 *Próximos Passos:*
Fique atento ao vencimento para garantir o pagamento em dia.

Em caso de dúvidas, entre em contato conosco.

Atenciosamente,
Equipe de Cobrança
"""
    
    # Envia via WhatsApp para o cliente
    whatsapp_service = WhatsAppService()
    result = whatsapp_service.send_message(telefone, mensagem)
    
    if result.get('success'):
        logger.info(f'Mensagem WhatsApp enviada para {cliente.name} ({telefone}) sobre recorrência {recorrencia.asaas_id}')
    else:
        logger.error(f'Erro ao enviar WhatsApp para {cliente.name}: {result.get("error")}')
    
    # Envia notificação para números configurados em WHATSAPP_NUMBERS
    from django.conf import settings as django_settings
    test_numbers = getattr(django_settings, 'WHATSAPP_NUMBERS', [])
    if test_numbers:
        notification_message = f"""🔔 *Nova Recorrência Criada*

📋 *Detalhes:*
• Cliente: {cliente.name}
• Descrição: {recorrencia.description}
• Valor: R$ {recorrencia.value:.2f}
• Ciclo: {ciclo_nome}
• Próximo Vencimento: {recorrencia.next_due_date.strftime('%d/%m/%Y')}
"""
        if link_pagamento and link_pagamento.url:
            notification_message += f"• Link de Pagamento: {link_pagamento.url}\n"
        
        notification_message += f"""
Sistema de Gestão Asaas
"""
        
        for number in test_numbers:
            number = number.strip()
            if number:
                result_notif = whatsapp_service.send_message(number, notification_message)
                if result_notif.get('success'):
                    logger.info(f'Notificação enviada para número de teste {number}')
                else:
                    logger.warning(f'Erro ao enviar notificação para {number}: {result_notif.get("error")}')


# ==================== LINKS DE PAGAMENTO INICIAL DA RECORRÊNCIA ====================

@login_required(login_url='login')
def recorrencia_link_primeira_cobranca(request, pk):
    """
    Opção 1: Gera link de pagamento da primeira cobrança da recorrência
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if not recorrencia.asaas_id:
        messages.error(request, 'Esta recorrência não está sincronizada com o Asaas.')
        return redirect('recorrencia_list')
    
    try:
        asaas_service = AsaasService()
        
        # Buscar as cobranças da assinatura
        result = asaas_service.list_subscription_payments(recorrencia.asaas_id, limit=1)
        
        if not result.get('success'):
            messages.error(request, f'Erro ao buscar cobranças: {result.get("error")}')
            return redirect('recorrencia_list')
        
        payments = result.get('data', [])
        if not payments:
            messages.warning(request, 'Nenhuma cobrança encontrada para esta recorrência.')
            return redirect('recorrencia_list')
        
        # Pegar a primeira cobrança
        first_payment = payments[0]
        payment_id = first_payment.get('id')
        
        # Buscar detalhes da cobrança para pegar a URL
        payment_details = asaas_service.get_payment(payment_id)
        
        if payment_details.get('success'):
            data = payment_details['data']
            invoice_url = data.get('invoiceUrl')
            
            if invoice_url:
                messages.success(request, f'Link da primeira cobrança gerado com sucesso!')
                # Redirecionar para a URL ou mostrar em uma modal
                return redirect(invoice_url)
            else:
                messages.warning(request, 'URL de pagamento não disponível ainda.')
        else:
            messages.error(request, f'Erro ao buscar detalhes da cobrança: {payment_details.get("error")}')
    
    except Exception as e:
        logger.error(f'Erro ao gerar link da primeira cobrança: {str(e)}')
        messages.error(request, f'Erro ao gerar link: {str(e)}')
    
    return redirect('recorrencia_list')


@login_required(login_url='login')
def recorrencia_enviar_link_inicial_whatsapp(request, pk):
    """
    Opção 2: Envia link da primeira cobrança por WhatsApp
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if not recorrencia.asaas_id:
        messages.error(request, 'Esta recorrência não está sincronizada com o Asaas.')
        return redirect('recorrencia_list')
    
    if not recorrencia.cliente:
        messages.error(request, 'Cliente não encontrado.')
        return redirect('recorrencia_list')
    
    # Verificar se cliente tem telefone
    phone = recorrencia.cliente.mobilePhone or recorrencia.cliente.phone
    if not phone:
        messages.error(request, 'Cliente não possui telefone cadastrado.')
        return redirect('recorrencia_list')
    
    try:
        asaas_service = AsaasService()
        whatsapp_service = WhatsAppService()
        
        # Buscar primeira cobrança
        result = asaas_service.list_subscription_payments(recorrencia.asaas_id, limit=1)
        
        if not result.get('success'):
            messages.error(request, f'Erro ao buscar cobranças: {result.get("error")}')
            return redirect('recorrencia_list')
        
        payments = result.get('data', [])
        if not payments:
            messages.warning(request, 'Nenhuma cobrança encontrada.')
            return redirect('recorrencia_list')
        
        first_payment = payments[0]
        payment_id = first_payment.get('id')
        
        # Buscar detalhes
        payment_details = asaas_service.get_payment(payment_id)
        
        if not payment_details.get('success'):
            messages.error(request, f'Erro ao buscar detalhes: {payment_details.get("error")}')
            return redirect('recorrencia_list')
        
        data = payment_details['data']
        invoice_url = data.get('invoiceUrl')
        due_date = data.get('dueDate')
        value = data.get('value')
        
        if not invoice_url:
            messages.warning(request, 'URL de pagamento não disponível.')
            return redirect('recorrencia_list')
        
        # Montar mensagem
        message = f"""🔔 *Primeira Cobrança da sua Assinatura*

Olá, {recorrencia.cliente.name}!

📋 *Detalhes:*
• Descrição: {recorrencia.description}
• Valor: R$ {value:.2f}
• Vencimento: {datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%Y')}

💳 *Link de Pagamento:*
{invoice_url}

Esta é a primeira cobrança da sua assinatura.

_Sistema de Gestão Asaas_"""
        
        # Enviar WhatsApp
        result_whats = whatsapp_service.send_message(phone, message)
        
        if result_whats.get('success'):
            messages.success(request, f'Link enviado com sucesso para {phone}!')
        else:
            messages.error(request, f'Erro ao enviar WhatsApp: {result_whats.get("error")}')
    
    except Exception as e:
        logger.error(f'Erro ao enviar link inicial: {str(e)}')
        messages.error(request, f'Erro: {str(e)}')
    
    return redirect('recorrencia_list')


@login_required(login_url='login')
def recorrencia_checkout_assinatura(request, pk):
    """
    Opção 3: Cria um checkout de assinatura (link profissional do Asaas)
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk)
    
    if not recorrencia.asaas_id:
        messages.error(request, 'Esta recorrência não está sincronizada com o Asaas.')
        return redirect('recorrencia_list')
    
    try:
        asaas_service = AsaasService()
        
        # Criar link de pagamento específico para esta assinatura
        payment_link_data = {
            'name': f"Checkout - {recorrencia.description}",
            'description': f"Assinatura: {recorrencia.description}",
            'billingType': recorrencia.billing_type,
            'chargeType': 'RECURRENT',  # Tipo recorrente
            'value': float(recorrencia.value),
            'dueDateLimitDays': 30,
        }
        
        # Adicionar cliente se existir
        if recorrencia.cliente and recorrencia.cliente.asaas_id:
            payment_link_data['customer'] = recorrencia.cliente.asaas_id
        
        # Criar link
        result = asaas_service.create_payment_link(payment_link_data)
        
        if result.get('success'):
            data = result['data']
            checkout_url = data.get('url')
            
            # Salvar no banco
            LinkPagamento.objects.create(
                nome=payment_link_data['name'],
                descricao=payment_link_data['description'],
                valor=recorrencia.value,
                billing_type=recorrencia.billing_type,
                charge_type='RECURRENT',
                cliente=recorrencia.cliente,
                due_date_limit_days=30,
                asaas_id=data.get('id'),
                url=checkout_url,
                status=data.get('status', 'ACTIVE'),
                synced_with_asaas=True,
            )
            
            messages.success(request, 'Checkout de assinatura criado com sucesso!')
            
            # Redirecionar para o checkout ou mostrar URL
            return redirect(checkout_url)
        else:
            messages.error(request, f'Erro ao criar checkout: {result.get("error")}')
    
    except Exception as e:
        logger.error(f'Erro ao criar checkout de assinatura: {str(e)}')
        messages.error(request, f'Erro: {str(e)}')
    
    return redirect('recorrencia_list')
