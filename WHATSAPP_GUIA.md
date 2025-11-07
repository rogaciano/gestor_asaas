# 📱 Guia de Integração WhatsApp

## 🎯 Objetivo

Enviar mensagens automáticas via WhatsApp para clientes quando uma recorrência é criada.

## ⚙️ Configuração

### 1. Adicione as variáveis no arquivo `.env`

```env
# WhatsApp API Configuration
# Provider: evolution, whatsapp_business, ou custom
WHATSAPP_PROVIDER=evolution

# Para Evolution API
WHATSAPP_API_URL=http://seu-servidor:8080
WHATSAPP_API_KEY=sua_chave_api_aqui
WHATSAPP_INSTANCE_ID=seu_instance_id_aqui

# Para WhatsApp Business API (alternativa)
WHATSAPP_TOKEN=seu_token_bearer_aqui
```

### 2. Configuração por Provedor

#### Evolution API (Recomendado)

```env
WHATSAPP_PROVIDER=evolution
WHATSAPP_API_URL=http://localhost:8080
WHATSAPP_API_KEY=sua_chave_api
WHATSAPP_INSTANCE_ID=default
```

**Endpoints Evolution API:**
- `POST /message/sendText/{instanceId}` - Enviar mensagem de texto
- `POST /message/sendTemplate/{instanceId}` - Enviar template

#### WhatsApp Business API

```env
WHATSAPP_PROVIDER=whatsapp_business
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_TOKEN=seu_token_bearer
```

#### API Customizada

```env
WHATSAPP_PROVIDER=custom
WHATSAPP_API_URL=https://sua-api.com
WHATSAPP_API_KEY=sua_chave
```

## 📋 Como Funciona

### Quando uma Recorrência é Criada

1. **Sistema cria a recorrência no Asaas**
2. **Se a recorrência foi criada com sucesso**, automaticamente:
   - Verifica se o cliente tem telefone cadastrado
   - Formata a mensagem com os detalhes da recorrência
   - Envia via WhatsApp para o cliente

### Mensagem Padrão

A mensagem inclui:
- ✅ Nome do cliente
- ✅ Descrição da recorrência
- ✅ Valor
- ✅ Ciclo (Mensal, Semanal, etc.)
- ✅ Forma de pagamento
- ✅ Próximo vencimento
- ✅ Data de término (se houver)
- ✅ Total de cobranças (se houver)

### Exemplo de Mensagem

```
Olá João Silva! 👋

Sua recorrência foi criada com sucesso! ✅

📋 *Detalhes da Recorrência:*
• Descrição: Plano Premium
• Valor: R$ 99.90
• Ciclo: Mensal
• Forma de Pagamento: Boleto Bancário
• Próximo Vencimento: 01/12/2025

📌 *Próximos Passos:*
Fique atento ao vencimento para garantir o pagamento em dia.

Em caso de dúvidas, entre em contato conosco.

Atenciosamente,
Equipe de Cobrança
```

## 🔧 Personalização

### Modificar a Mensagem

Edite a função `enviar_whatsapp_recorrencia()` em `asaas_app/views.py`:

```python
def enviar_whatsapp_recorrencia(recorrencia):
    # ... código existente ...
    
    mensagem = f"""Sua mensagem personalizada aqui"""
    
    # ... resto do código ...
```

### Adicionar Link de Pagamento

Se quiser incluir o link de pagamento na mensagem:

```python
# Adicione após criar a recorrência
if result.get('success'):
    # Busca link de pagamento se existir
    link_pagamento = LinkPagamento.objects.filter(
        cliente=recorrencia.cliente,
        charge_type='RECURRENT'
    ).first()
    
    if link_pagamento and link_pagamento.url:
        mensagem += f"\n🔗 Link de Pagamento: {link_pagamento.url}\n"
```

## 🧪 Testando

### 1. Verifique as Configurações

```python
python manage.py shell
```

```python
from django.conf import settings

print(f"API URL: {settings.WHATSAPP_API_URL}")
print(f"Provider: {settings.WHATSAPP_PROVIDER}")
print(f"API Key configurada: {bool(settings.WHATSAPP_API_KEY)}")
```

### 2. Teste o Envio

```python
from asaas_app.whatsapp_service import WhatsAppService

whatsapp = WhatsAppService()
result = whatsapp.send_message("11987654321", "Mensagem de teste")

if result.get('success'):
    print("✅ Mensagem enviada com sucesso!")
else:
    print(f"❌ Erro: {result.get('error')}")
```

### 3. Crie uma Recorrência

1. Acesse o sistema
2. Vá em **Recorrências** → **Nova Recorrência**
3. Preencha os dados (certifique-se que o cliente tem telefone)
4. Salve a recorrência
5. Verifique se a mensagem foi enviada

## 📝 Requisitos

### Para o Cliente

- ✅ Cliente deve ter **telefone** ou **celular** cadastrado
- ✅ Cliente deve estar **sincronizado com Asaas** (ter `asaas_id`)
- ✅ Recorrência deve ser **criada com sucesso no Asaas**

### Para o Sistema

- ✅ WhatsApp API configurada no `.env`
- ✅ API acessível (servidor rodando)
- ✅ Credenciais válidas

## 🐛 Troubleshooting

### "WhatsApp API não configurada"

**Solução:** Verifique se as variáveis estão no `.env`:
```env
WHATSAPP_API_URL=http://...
WHATSAPP_API_KEY=...
```

### "Cliente não possui telefone cadastrado"

**Solução:** Adicione o telefone do cliente no cadastro:
- Acesse **Clientes** → **Editar Cliente**
- Preencha **Celular** ou **Telefone**

### "Erro ao enviar WhatsApp"

**Verifique:**
1. API está acessível? (`curl http://seu-servidor:8080`)
2. Credenciais estão corretas?
3. Número está no formato correto?
4. Instância está ativa?

### Logs

Os logs são salvos no console do Django. Procure por:
- `INFO: Mensagem WhatsApp enviada para...`
- `ERROR: Erro ao enviar WhatsApp...`

## 🔐 Segurança

- ✅ Nunca commite o `.env` no Git
- ✅ Use variáveis de ambiente em produção
- ✅ Valide números antes de enviar
- ✅ Implemente rate limiting se necessário

## 📚 Próximos Passos

- [ ] Adicionar envio para outros eventos (pagamento recebido, vencimento, etc.)
- [ ] Templates de mensagem personalizáveis
- [ ] Histórico de mensagens enviadas
- [ ] Agendamento de mensagens
- [ ] Suporte a mídia (imagens, documentos)

## 💡 Dicas

1. **Teste primeiro** com uma recorrência de teste
2. **Use Evolution API** para desenvolvimento local
3. **Valide números** antes de enviar em produção
4. **Personalize mensagens** conforme seu negócio
5. **Monitore logs** para identificar problemas

---

**Desenvolvido com ❤️ para automatizar sua comunicação!**

