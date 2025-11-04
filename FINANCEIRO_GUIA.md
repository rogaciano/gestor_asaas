# 💰 Módulo Financeiro - Guia Completo

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Instalação](#instalação)
3. [Funcionalidades](#funcionalidades)
4. [Como Usar](#como-usar)
5. [Regras de Categorização](#regras-de-categorização)
6. [Conciliação](#conciliação)
7. [Relatórios](#relatórios)
8. [Dicas e Boas Práticas](#dicas-e-boas-práticas)

---

## 🎯 Visão Geral

O módulo financeiro oferece uma solução completa para gerenciar suas finanças integradas ao Asaas:

### Recursos Principais
- **Plano de Contas**: Organize receitas e despesas em categorias hierárquicas
- **Movimentações**: Importe e gerencie todas as transações financeiras
- **Categorização Automática**: Configure regras inteligentes para classificação automática
- **Conciliação**: Interface rápida para categorizar movimentações pendentes
- **Relatórios**: Dashboards com análises detalhadas e visualizações

---

## 🚀 Instalação

### 1. Migrations
As migrations já foram aplicadas. Se precisar reaplicar:

```bash
python manage.py migrate
```

### 2. Popular Plano de Contas
Execute o comando para criar categorias padrão:

```bash
python manage.py popular_plano_contas
```

Isso criará 33 categorias organizadas em:
- **Receitas**: Operacionais, Financeiras
- **Despesas**: Operacionais, Vendas, Financeiras, Administrativas, Impostos

---

## 📊 Funcionalidades

### 1. Plano de Contas
**Acesso**: Menu Financeiro → Plano de Contas

#### O que é?
Sistema de categorização hierárquico para classificar receitas e despesas.

#### Campos:
- **Código**: Identificador único (ex: 1.1.01, 2.3.02)
- **Nome**: Nome da categoria
- **Tipo**: RECEITA ou DESPESA
- **Categoria Pai**: Categoria superior (hierarquia)
- **Descrição**: Detalhes adicionais
- **Ativa**: Se a categoria está em uso

#### Exemplos:
```
1.0 RECEITAS (Pai)
  └─ 1.1 Receitas Operacionais (Filho)
      └─ 1.1.01 Vendas de Produtos (Neto)
      └─ 1.1.02 Prestação de Serviços (Neto)

2.0 DESPESAS (Pai)
  └─ 2.3 Despesas Financeiras (Filho)
      └─ 2.3.02 Taxas Asaas (Neto)
```

---

### 2. Movimentações
**Acesso**: Menu Financeiro → Movimentações

#### O que são?
Todas as transações financeiras importadas do Asaas ou criadas manualmente.

#### Tipos de Movimentação:
- `PAYMENT`: Pagamento Recebido
- `PAYMENT_FEE`: Taxa de Pagamento
- `TRANSFER`: Transferência
- `TRANSFER_FEE`: Taxa de Transferência
- `REFUND`: Reembolso
- `CHARGEBACK`: Chargeback
- `ANTICIPATION`: Antecipação
- `ANTICIPATION_FEE`: Taxa de Antecipação
- `OTHER`: Outro

#### Status de Conciliação:
- **Não Conciliado**: Sem categoria atribuída
- **Conciliado Auto**: Categorizado por regra automática
- **Conciliado Manual**: Categorizado manualmente

#### Filtros Disponíveis:
- Pesquisa por descrição ou cliente
- Período (data início/fim)
- Tipo de movimentação
- Status de conciliação
- Categoria

---

### 3. Importação de Movimentações
**Acesso**: Movimentações → Importar do Asaas

#### Como funciona:
1. Selecione o período (data início e fim)
2. Clique em "Importar"
3. O sistema buscará todas as transações do Asaas
4. Movimentações novas serão criadas
5. Movimentações existentes serão atualizadas
6. Regras de categorização serão aplicadas automaticamente

#### Dados Importados:
- ID do Asaas (para sincronização)
- Data da transação
- Descrição
- Tipo
- Valor
- Cliente relacionado (se existir)
- Dados completos do Asaas (JSON)

---

### 4. Regras de Categorização Automática
**Acesso**: Menu Financeiro → Regras Automáticas

#### O que são?
Regras inteligentes que categorizam automaticamente movimentações com base em condições.

#### Como criar uma regra:

**Exemplo 1: Taxas Asaas**
```
Nome: Taxa Asaas → Despesas Taxas
Campo: Tipo de Movimentação
Operador: Igual a
Valor: PAYMENT_FEE
Categoria: 2.3.02 - Taxas Asaas
Prioridade: 10
```

**Exemplo 2: Cliente Específico**
```
Nome: Pagamentos João Silva
Campo: Cliente
Operador: Contém
Valor: João Silva
Categoria: 1.1.03 - Recorrências
Prioridade: 5
```

**Exemplo 3: Descrição**
```
Nome: Transferências Bancárias
Campo: Descrição
Operador: Contém
Valor: Transferência
Categoria: 2.3.01 - Taxas Bancárias
Prioridade: 3
```

#### Operadores Disponíveis:
- **Contém**: Verifica se o texto está presente
- **Igual a**: Comparação exata
- **Começa com**: Verifica o início do texto
- **Termina com**: Verifica o final do texto

#### Prioridade:
- Regras com **maior prioridade** são executadas primeiro
- Use 0-10 (0 = baixa, 10 = alta)
- Se múltiplas regras se aplicam, a primeira (maior prioridade) vence

#### Aplicar Regras:
- **Automático**: Ao importar movimentações
- **Manual**: Botão "Aplicar Agora" na lista de regras

---

### 5. Conciliação Manual
**Acesso**: Menu Financeiro → Conciliação

#### Interface Rápida:
1. Visualize movimentações não conciliadas
2. Selecione a categoria no dropdown
3. Clique em "Conciliar"
4. A movimentação é removida da lista instantaneamente

#### Vantagens:
- Interface otimizada para velocidade
- Sem necessidade de entrar na tela de edição
- Processamento via AJAX (sem reload da página)

---

### 6. Relatórios
**Acesso**: Menu Financeiro → Relatórios

#### Métricas Disponíveis:

**1. Cards de Resumo**
- Total de Receitas (período)
- Total de Despesas (período)
- Saldo (Receitas - Despesas)
- Movimentações Não Conciliadas

**2. Por Categoria**
- Gráfico de barras por categoria
- Valor total e quantidade de transações
- Separado por receitas e despesas

**3. Evolução Mensal**
- Tabela com receitas, despesas e saldo por mês
- Identifica meses positivos e negativos
- Útil para análise de tendências

**4. Status de Conciliação**
- Quantidade de movimentações:
  - Não conciliadas
  - Conciliadas automaticamente
  - Conciliadas manualmente

**5. Top 10 Clientes**
- Clientes que mais geraram receitas
- Quantidade de transações por cliente
- Valor total por cliente

#### Filtros:
- Período (data início/fim)
- Padrão: últimos 30 dias

---

## 🎓 Como Usar

### Fluxo Recomendado

#### 1️⃣ **Configuração Inicial**

```bash
# 1. Popular plano de contas
python manage.py popular_plano_contas

# 2. Ajustar categorias conforme seu negócio
# Acesse: Financeiro → Plano de Contas
# - Adicione categorias específicas
# - Desative categorias não utilizadas
```

#### 2️⃣ **Criar Regras de Categorização**

Acesse: Financeiro → Regras Automáticas

Crie regras para os casos mais comuns:
- Taxas do Asaas
- Clientes principais
- Tipos de transação

**Dica**: Comece com as regras mais específicas (alta prioridade) e depois as genéricas (baixa prioridade).

#### 3️⃣ **Importar Movimentações**

Acesse: Financeiro → Movimentações → Importar

1. Defina o período (ex: último mês)
2. Importe as transações
3. O sistema aplicará as regras automaticamente

#### 4️⃣ **Conciliar Pendências**

Acesse: Financeiro → Conciliação

1. Categorize rapidamente as movimentações não conciliadas
2. Identifique padrões e crie novas regras

#### 5️⃣ **Analisar Relatórios**

Acesse: Financeiro → Relatórios

1. Visualize o desempenho financeiro
2. Identifique categorias com maiores valores
3. Analise evolução mensal
4. Verifique top clientes

---

## 🔧 Regras de Categorização

### Exemplos Práticos

#### Regra 1: Todas as Taxas Asaas
```
Nome: Taxa Asaas
Campo: Tipo
Operador: Igual a
Valor: PAYMENT_FEE
Categoria: 2.3.02 - Taxas Asaas
Prioridade: 10
Ativa: ✓
```

#### Regra 2: Recorrências por Cliente
```
Nome: Recorrência - João Silva
Campo: Cliente
Operador: Contém
Valor: João Silva
Categoria: 1.1.03 - Recorrências
Prioridade: 8
Ativa: ✓
```

#### Regra 3: Descrição com Palavra-Chave
```
Nome: Transferências PIX
Campo: Descrição
Operador: Contém
Valor: PIX
Categoria: 2.3.01 - Taxas Bancárias
Prioridade: 5
Ativa: ✓
```

### Testando Regras

1. **Crie a regra**
2. **Importe movimentações** ou clique em **"Aplicar Agora"**
3. **Verifique** se as movimentações foram categorizadas corretamente
4. **Ajuste** a regra se necessário (prioridade, operador, valor)

---

## ✅ Conciliação

### Métodos de Conciliação

#### 1. **Automática (Regras)**
- Aplicada durante a importação
- Pode ser reaplicada manualmente
- Status: "Conciliado Auto"

#### 2. **Rápida (Interface de Conciliação)**
- Seleciona categoria e concilia em 1 clique
- Ideal para grandes volumes
- Status: "Conciliado Manual"

#### 3. **Detalhada (Edição de Movimentação)**
- Acesso completo a todos os campos
- Permite adicionar observações
- Status: "Conciliado Manual"

### Boas Práticas

✅ **Concilie regularmente** (semanal ou mensal)  
✅ **Crie regras para padrões recorrentes**  
✅ **Use observações para casos especiais**  
✅ **Revise relatórios após conciliação**

---

## 📈 Relatórios

### Como Analisar

#### 1. **Visão Geral (Cards)**
- Receitas, Despesas e Saldo
- Rápido indicador de saúde financeira

#### 2. **Por Categoria**
- Identifique onde o dinheiro está sendo gasto
- Compare com períodos anteriores
- Tome decisões sobre corte de custos

#### 3. **Evolução Mensal**
- Tendência de crescimento ou redução
- Sazonalidade
- Planejamento financeiro

#### 4. **Top Clientes**
- Clientes mais valiosos
- Foque em retenção e upsell
- Identifique clientes em risco

---

## 💡 Dicas e Boas Práticas

### Organização

1. **Use códigos hierárquicos consistentes**
   - `1.x` para receitas
   - `2.x` para despesas
   - `x.1`, `x.2` para subcategorias

2. **Nomes claros e objetivos**
   - ✅ "Taxas Asaas"
   - ❌ "Taxas várias"

3. **Hierarquia não muito profunda**
   - Ideal: 3 níveis (Pai → Filho → Neto)
   - Evite: 5+ níveis

### Regras de Categorização

1. **Prioridade decrescente**
   - 10: Regras muito específicas
   - 5: Regras moderadas
   - 1: Regras genéricas

2. **Teste antes de ativar**
   - Crie a regra
   - Teste com dados reais
   - Ative se funcionar corretamente

3. **Revise periodicamente**
   - Verifique quantas vezes foi aplicada
   - Desative regras obsoletas

### Importação

1. **Importe periodicamente**
   - Semanal ou mensal
   - Não deixe acumular

2. **Revise após importação**
   - Verifique movimentações não conciliadas
   - Crie regras para padrões novos

3. **Backup antes de grandes importações**
   - Use `python manage.py dumpdata > backup.json`

### Conciliação

1. **Priorize conciliação rápida**
   - Use a interface de conciliação para agilidade
   - Reserve a edição detalhada para casos especiais

2. **Adicione observações quando relevante**
   - Explique categorizações não óbvias
   - Útil para auditoria futura

3. **Meta: 100% conciliado**
   - Todas as movimentações devem ter categoria
   - Facilita análise e relatórios precisos

### Relatórios

1. **Análise periódica**
   - Mensal: Análise detalhada
   - Semanal: Verificação rápida

2. **Compare períodos**
   - Mês atual vs anterior
   - Ano atual vs anterior

3. **Exporte dados se necessário**
   - Use o admin do Django
   - Ou crie relatórios personalizados

---

## 🆘 Suporte

### Problemas Comuns

#### "Movimentação não foi categorizada automaticamente"
✅ Verifique se há uma regra ativa que se aplica  
✅ Teste a regra manualmente  
✅ Verifique a prioridade (regras com maior prioridade vêm primeiro)

#### "Relatório sem dados"
✅ Verifique o período selecionado  
✅ Confirme que há movimentações importadas  
✅ Verifique se as movimentações estão conciliadas

#### "Categoria não aparece nos filtros"
✅ Verifique se a categoria está ativa  
✅ Confirme que há movimentações vinculadas a ela

---

## 🎯 Próximos Passos

Após dominar o módulo financeiro, explore:

1. **Integrações Avançadas**
   - Webhooks do Asaas
   - Notificações automáticas

2. **Automações**
   - Relatórios por email
   - Alertas de movimentações não conciliadas

3. **Análises Personalizadas**
   - Gráficos customizados
   - Exportação para Excel/CSV

---

## 📚 Referências

- [Documentação Asaas API](https://docs.asaas.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Desenvolvido com ❤️ para simplificar sua gestão financeira!**

