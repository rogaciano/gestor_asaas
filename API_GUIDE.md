# 🔌 Guia de Integração com API do Asaas

## 📝 Configuração Inicial

### 1. Obter API Key

#### Ambiente Sandbox (Testes)
1. Acesse: https://sandbox.asaas.com
2. Crie uma conta gratuita
3. Faça login
4. Vá em **Integrações** > **API Key**
5. Copie sua chave da API Sandbox

#### Ambiente Produção
1. Acesse: https://www.asaas.com
2. Faça login na sua conta
3. Vá em **Integrações** > **API Key**
4. Copie sua chave da API de Produção

### 2. Configurar no Sistema

Edite o arquivo `.env`:

```env
# Para Sandbox (Testes)
ASAAS_API_KEY=sua_chave_sandbox_aqui
ASAAS_API_URL=https://sandbox.asaas.com/api/v3

# Para Produção
ASAAS_API_KEY=sua_chave_producao_aqui
ASAAS_API_URL=https://api.asaas.com/v3
```

## 🔄 Funcionalidades da API

### Clientes (Customers)

#### Criar Cliente
```python
# O sistema faz automaticamente ao salvar um cliente
POST /customers
{
  "name": "João Silva",
  "cpfCnpj": "12345678901",
  "email": "joao@example.com",
  "phone": "1140401234",
  "mobilePhone": "11987654321",
  "address": "Rua das Flores",
  "addressNumber": "123",
  "complement": "Apto 45",
  "province": "Centro",
  "postalCode": "01310-100"
}
```

#### Atualizar Cliente
```python
# Sincronização automática ao editar
PUT /customers/{id}
```

#### Buscar Cliente
```python
GET /customers/{id}
```

#### Deletar Cliente
```python
DELETE /customers/{id}
```

### Assinaturas (Subscriptions)

#### Criar Assinatura
```python
# Criação automática ao salvar recorrência
POST /subscriptions
{
  "customer": "cus_000001234567",
  "billingType": "BOLETO",
  "value": 99.90,
  "nextDueDate": "2025-12-01",
  "cycle": "MONTHLY",
  "description": "Plano Premium"
}
```

#### Ciclos Disponíveis
- `WEEKLY` - Semanal
- `BIWEEKLY` - Quinzenal
- `MONTHLY` - Mensal
- `QUARTERLY` - Trimestral
- `SEMIANNUALLY` - Semestral
- `YEARLY` - Anual

#### Formas de Pagamento
- `BOLETO` - Boleto Bancário
- `CREDIT_CARD` - Cartão de Crédito
- `PIX` - PIX
- `UNDEFINED` - Indefinido

#### Atualizar Assinatura
```python
PUT /subscriptions/{id}
```

#### Cancelar Assinatura
```python
DELETE /subscriptions/{id}
```

## 🎯 Fluxo de Trabalho

### Cadastro Completo

```
1. Cadastrar Cliente no Sistema
   ↓
2. Sistema cria Cliente no Asaas
   ↓
3. Asaas retorna ID do Cliente
   ↓
4. Sistema salva ID localmente
   ↓
5. Criar Recorrência no Sistema
   ↓
6. Sistema cria Assinatura no Asaas
   ↓
7. Asaas retorna ID da Assinatura
   ↓
8. Sistema salva ID localmente
   ↓
9. ✅ Cliente e Recorrência sincronizados!
```

## 🛠️ Tratamento de Erros

### Erros Comuns

#### 1. "Invalid access_token"
**Causa:** API Key incorreta ou inválida
**Solução:** 
- Verifique a API Key no `.env`
- Confirme se está usando a chave correta (sandbox vs produção)
- Gere uma nova chave no Asaas se necessário

#### 2. "Customer already exists"
**Causa:** CPF/CNPJ já cadastrado no Asaas
**Solução:**
- Use um CPF/CNPJ diferente
- Ou busque o cliente existente no Asaas

#### 3. "Invalid cpfCnpj"
**Causa:** CPF/CNPJ em formato incorreto
**Solução:**
- Use apenas números: "12345678901"
- Remova pontos, traços e barras

#### 4. "Customer not found"
**Causa:** Cliente não existe no Asaas
**Solução:**
- Sincronize o cliente primeiro
- Verifique se o asaas_id está correto

#### 5. "Unauthorized"
**Causa:** Problemas de autenticação
**Solução:**
- Verifique se a API Key está no header correto
- Confirme se a conta Asaas está ativa

## 📊 Limites da API

### Rate Limiting
- **Sandbox:** Ilimitado para testes
- **Produção:** Depende do seu plano Asaas

### Timeouts
- Conexão: 10 segundos
- Resposta: 30 segundos

## 🔐 Segurança

### Boas Práticas

✅ **Nunca exponha sua API Key**
```python
# ❌ Errado
api_key = "sua_chave_aqui"  # No código

# ✅ Correto
api_key = config('ASAAS_API_KEY')  # Do .env
```

✅ **Use HTTPS sempre**
```python
# Sempre use https://
ASAAS_API_URL=https://api.asaas.com/v3
```

✅ **Valide dados antes de enviar**
```python
# Valide CPF/CNPJ, email, etc.
if not validate_cpf(cpf):
    return error
```

✅ **Guarde os IDs retornados**
```python
# Salve customer_id e subscription_id
cliente.asaas_id = response['id']
cliente.save()
```

## 🧪 Testando a Integração

### 1. Teste de Conexão

Execute no shell do Django:
```bash
python manage.py shell
```

```python
from asaas_app.services import AsaasService
from django.conf import settings

# Verificar configuração
print(settings.ASAAS_API_KEY[:10] + "...")  # Primeiros 10 caracteres
print(settings.ASAAS_API_URL)

# Testar serviço
service = AsaasService()
# O serviço está pronto!
```

### 2. Teste de Cliente

Crie um cliente pelo sistema e verifique:
- ✅ Cliente aparece na lista
- ✅ Badge "Sincronizado" está verde
- ✅ asaas_id foi salvo

### 3. Teste de Recorrência

Crie uma recorrência e verifique:
- ✅ Recorrência foi criada
- ✅ Status "Ativa"
- ✅ Sincronizada com Asaas

## 📚 Recursos Adicionais

### Documentação Oficial
- **API Docs:** https://docs.asaas.com
- **Referência:** https://asaasv3.docs.apiary.io/
- **Sandbox:** https://sandbox.asaas.com

### Status da API
- **Status Page:** https://status.asaas.com

### Suporte
- **Email:** suporte@asaas.com
- **Telefone:** (11) 4007-2847
- **WhatsApp:** Disponível no site

## 💡 Dicas Importantes

### CPF/CNPJ de Teste
Para testes no sandbox, você pode usar:
- CPFs gerados online (válidos, mas fictícios)
- CNPJs de teste

### Ambientes
- **Sempre teste no Sandbox primeiro!**
- Sandbox não gera cobranças reais
- Dados do Sandbox são isolados

### Logs
O sistema registra erros de API em:
```python
import logging
logger = logging.getLogger(__name__)
# Verifique o console do servidor
```

## 🔄 Webhook (Futuro)

O Asaas pode notificar seu sistema sobre:
- Pagamentos recebidos
- Cobranças vencidas
- Assinaturas canceladas
- etc.

Para implementar, você precisará:
1. Criar uma view para receber webhooks
2. Validar a assinatura do webhook
3. Processar os eventos
4. Configurar a URL no Asaas

---

**Pronto!** Agora você sabe tudo sobre a integração com a API do Asaas! 🚀

