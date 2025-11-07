from django.db import models


class Cliente(models.Model):
    """Modelo para armazenar informações de clientes"""
    
    # Campos obrigatórios
    name = models.CharField('Nome', max_length=255)
    cpfCnpj = models.CharField('CPF/CNPJ', max_length=18, unique=True)
    email = models.EmailField('E-mail')
    
    # Campos opcionais
    phone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    mobilePhone = models.CharField('Celular', max_length=20, blank=True, null=True)
    address = models.CharField('Endereço', max_length=255, blank=True, null=True)
    addressNumber = models.CharField('Número', max_length=10, blank=True, null=True)
    complement = models.CharField('Complemento', max_length=100, blank=True, null=True)
    province = models.CharField('Bairro', max_length=100, blank=True, null=True)
    postalCode = models.CharField('CEP', max_length=9, blank=True, null=True)
    observations = models.TextField('Observações', blank=True, null=True, help_text='Id do cliente no TalkIAChat')
    
    # Campos de controle
    asaas_id = models.CharField('ID Asaas', max_length=50, blank=True, null=True, unique=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    synced_with_asaas = models.BooleanField('Sincronizado com Asaas', default=False)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.cpfCnpj}"


class Recorrencia(models.Model):
    """Modelo para armazenar informações de recorrências (assinaturas)"""
    
    CYCLE_CHOICES = [
        ('WEEKLY', 'Semanal'),
        ('BIWEEKLY', 'Quinzenal'),
        ('MONTHLY', 'Mensal'),
        ('QUARTERLY', 'Trimestral'),
        ('SEMIANNUALLY', 'Semestral'),
        ('YEARLY', 'Anual'),
    ]
    
    BILLING_TYPE_CHOICES = [
        ('BOLETO', 'Boleto Bancário'),
        ('CREDIT_CARD', 'Cartão de Crédito'),
        ('PIX', 'Pix'),
        ('UNDEFINED', 'Perguntar ao Cliente'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Ativa'),
        ('INACTIVE', 'Inativa'),
        ('EXPIRED', 'Expirada'),
    ]
    
    # Relacionamento com cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='recorrencias', verbose_name='Cliente')
    
    # Campos da recorrência
    value = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    cycle = models.CharField('Ciclo', max_length=20, choices=CYCLE_CHOICES, default='MONTHLY')
    billing_type = models.CharField('Forma de Pagamento', max_length=20, choices=BILLING_TYPE_CHOICES, default='BOLETO')
    description = models.CharField('Descrição', max_length=255)
    
    # Datas
    next_due_date = models.DateField('Próximo Vencimento')
    end_date = models.DateField('Data de Término', blank=True, null=True)
    
    # Configurações adicionais
    max_payments = models.IntegerField('Número Máximo de Cobranças', blank=True, null=True, help_text='Deixe em branco para cobranças ilimitadas')
    
    # Campos de controle
    asaas_id = models.CharField('ID Asaas', max_length=50, blank=True, null=True, unique=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    synced_with_asaas = models.BooleanField('Sincronizado com Asaas', default=False)
    
    class Meta:
        verbose_name = 'Recorrência'
        verbose_name_plural = 'Recorrências'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.description} - {self.cliente.name} - R$ {self.value}"


class PlanoContas(models.Model):
    """Modelo para o Plano de Contas (categorias financeiras)"""
    
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    
    # Identificação
    codigo = models.CharField('Código', max_length=20, unique=True, help_text='Ex: 1.1.01, 2.3.05')
    nome = models.CharField('Nome', max_length=255)
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    
    # Hierarquia (para categorias pai/filho)
    categoria_pai = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                                     related_name='subcategorias', verbose_name='Categoria Pai')
    
    # Informações adicionais
    descricao = models.TextField('Descrição', blank=True, null=True)
    ativa = models.BooleanField('Ativa', default=True)
    
    # Controle
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Plano de Contas'
        verbose_name_plural = 'Plano de Contas'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Movimentacao(models.Model):
    """Modelo para movimentações financeiras (extratos/transações)"""
    
    TIPO_CHOICES = [
        ('PAYMENT', 'Pagamento Recebido'),
        ('PAYMENT_FEE', 'Taxa de Pagamento'),
        ('TRANSFER', 'Transferência'),
        ('TRANSFER_FEE', 'Taxa de Transferência'),
        ('REFUND', 'Reembolso'),
        ('CHARGEBACK', 'Chargeback'),
        ('ANTICIPATION', 'Antecipação'),
        ('ANTICIPATION_FEE', 'Taxa de Antecipação'),
        ('OTHER', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('CONFIRMED', 'Confirmado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    CONCILIACAO_CHOICES = [
        ('NAO_CONCILIADO', 'Não Conciliado'),
        ('CONCILIADO_AUTO', 'Conciliado Automaticamente'),
        ('CONCILIADO_MANUAL', 'Conciliado Manualmente'),
    ]
    
    # Dados da movimentação
    asaas_id = models.CharField('ID Asaas', max_length=50, unique=True, blank=True, null=True)
    data = models.DateField('Data')
    descricao = models.CharField('Descrição', max_length=500)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    
    # Relacionamentos
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='movimentacoes', verbose_name='Cliente')
    recorrencia = models.ForeignKey(Recorrencia, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='movimentacoes', verbose_name='Recorrência')
    
    # Conciliação
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='movimentacoes', verbose_name='Categoria')
    status_conciliacao = models.CharField('Status de Conciliação', max_length=20, 
                                         choices=CONCILIACAO_CHOICES, default='NAO_CONCILIADO')
    observacoes_conciliacao = models.TextField('Observações', blank=True, null=True)
    
    # Dados adicionais do Asaas
    dados_asaas = models.JSONField('Dados Completos do Asaas', blank=True, null=True)
    
    # Controle
    synced_with_asaas = models.BooleanField('Sincronizado com Asaas', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data', '-created_at']
    
    def __str__(self):
        return f"{self.data} - {self.descricao} - R$ {self.valor}"


class RegraCategorizacao(models.Model):
    """Modelo para regras de categorização automática"""
    
    CAMPO_CHOICES = [
        ('descricao', 'Descrição'),
        ('tipo', 'Tipo de Movimentação'),
        ('cliente', 'Cliente'),
    ]
    
    OPERADOR_CHOICES = [
        ('contem', 'Contém'),
        ('igual', 'Igual a'),
        ('comeca', 'Começa com'),
        ('termina', 'Termina com'),
    ]
    
    # Dados da regra
    nome = models.CharField('Nome da Regra', max_length=255)
    ativa = models.BooleanField('Ativa', default=True)
    prioridade = models.IntegerField('Prioridade', default=0, help_text='Maior = mais prioridade')
    
    # Condições
    campo = models.CharField('Campo', max_length=50, choices=CAMPO_CHOICES)
    operador = models.CharField('Operador', max_length=20, choices=OPERADOR_CHOICES)
    valor = models.CharField('Valor', max_length=255)
    
    # Ação
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.CASCADE, 
                                    related_name='regras', verbose_name='Categoria')
    
    # Estatísticas
    vezes_aplicada = models.IntegerField('Vezes Aplicada', default=0)
    
    # Controle
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Regra de Categorização'
        verbose_name_plural = 'Regras de Categorização'
        ordering = ['-prioridade', 'nome']
    
    def __str__(self):
        return f"{self.nome} → {self.plano_contas}"
    
    def aplicar(self, movimentacao):
        """Verifica se a regra se aplica à movimentação"""
        valor_campo = getattr(movimentacao, self.campo, '')
        
        if self.campo == 'cliente' and movimentacao.cliente:
            valor_campo = movimentacao.cliente.name
        
        valor_campo = str(valor_campo).lower()
        valor_regra = self.valor.lower()
        
        if self.operador == 'contem' and valor_regra in valor_campo:
            return True
        elif self.operador == 'igual' and valor_campo == valor_regra:
            return True
        elif self.operador == 'comeca' and valor_campo.startswith(valor_regra):
            return True
        elif self.operador == 'termina' and valor_campo.endswith(valor_regra):
            return True
        
        return False


class LinkPagamento(models.Model):
    """Modelo para armazenar links de pagamento do Asaas"""
    
    CHARGE_TYPE_CHOICES = [
        ('DETACHED', 'Avulso (valor fixo)'),
        ('INSTALLMENT', 'Parcelado'),
        ('RECURRENT', 'Recorrente (assinatura)'),
    ]
    
    BILLING_TYPE_CHOICES = [
        ('BOLETO', 'Boleto Bancário'),
        ('CREDIT_CARD', 'Cartão de Crédito'),
        ('PIX', 'Pix'),
        ('UNDEFINED', 'Perguntar ao Cliente'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Ativo'),
        ('INACTIVE', 'Inativo'),
        ('EXPIRED', 'Expirado'),
    ]
    
    # Dados básicos
    nome = models.CharField('Nome', max_length=255)
    descricao = models.TextField('Descrição', blank=True, null=True)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2, blank=True, null=True, 
                                help_text='Deixe em branco para permitir valor livre')
    billing_type = models.CharField('Forma de Pagamento', max_length=20, choices=BILLING_TYPE_CHOICES, 
                                    default='UNDEFINED')
    charge_type = models.CharField('Tipo de Cobrança', max_length=20, choices=CHARGE_TYPE_CHOICES, 
                                    default='DETACHED')
    
    # Configurações opcionais
    due_date_limit_days = models.IntegerField('Prazo de Vencimento (dias)', blank=True, null=True, 
                                              help_text='Quantos dias após o acesso o link expira')
    max_installments = models.IntegerField('Máximo de Parcelas', blank=True, null=True, 
                                          help_text='Apenas para cobrança parcelada')
    
    # Relacionamento com cliente (opcional)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='links_pagamento', verbose_name='Cliente')
    
    # Dados do Asaas
    asaas_id = models.CharField('ID Asaas', max_length=50, blank=True, null=True, unique=True)
    url = models.URLField('URL do Link', max_length=500, blank=True, null=True, 
                         help_text='Link público para compartilhar')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Controle
    synced_with_asaas = models.BooleanField('Sincronizado com Asaas', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Link de Pagamento'
        verbose_name_plural = 'Links de Pagamento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome} - {'R$ ' + str(self.valor) if self.valor else 'Valor Livre'}"
