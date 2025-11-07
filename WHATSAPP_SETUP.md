# 📱 Configuração WhatsApp - Resumo Rápido

## ✅ O que foi implementado

1. **Serviço de WhatsApp** (`asaas_app/whatsapp_service.py`)
   - Suporta Evolution API, WhatsApp Business API e APIs customizadas
   - Formatação automática de números
   - Tratamento de erros

2. **Integração com Recorrências**
   - Envio automático de mensagem quando recorrência é criada
   - Mensagem personalizada com detalhes da recorrência

3. **Configurações no Settings**
   - Variáveis de ambiente adicionadas
   - Suporte a múltiplos provedores

## 🔧 Configuração no .env

Adicione estas linhas no seu arquivo `.env`:

```env
# WhatsApp API Configuration
WHATSAPP_PROVIDER=evolution
WHATSAPP_API_URL=http://seu-servidor:8080
WHATSAPP_API_KEY=sua_chave_api_aqui
WHATSAPP_INSTANCE_ID=seu_instance_id_aqui
WHATSAPP_TOKEN=seu_token_aqui  # Opcional, para WhatsApp Business
```

## 📋 Variáveis Necessárias

| Variável | Descrição | Obrigatório | Exemplo |
|----------|-----------|-------------|---------|
| `WHATSAPP_PROVIDER` | Provedor da API (evolution, whatsapp_business, custom) | Sim | `evolution` |
| `WHATSAPP_API_URL` | URL base da API | Sim | `http://localhost:8080` |
| `WHATSAPP_API_KEY` | Chave de API | Sim | `sua_chave_aqui` |
| `WHATSAPP_INSTANCE_ID` | ID da instância (Evolution API) | Sim | `default` |
| `WHATSAPP_TOKEN` | Token Bearer (WhatsApp Business) | Opcional | `token_aqui` |

## 🚀 Como Usar

1. **Configure o .env** com suas credenciais
2. **Certifique-se** que o cliente tem telefone cadastrado
3. **Crie uma recorrência** normalmente
4. **O sistema enviará automaticamente** a mensagem via WhatsApp

## 📝 Exemplo de Mensagem

Quando uma recorrência é criada, o cliente recebe:

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

## 🧪 Teste Rápido

```python
python manage.py shell
```

```python
from asaas_app.whatsapp_service import WhatsAppService

whatsapp = WhatsAppService()
result = whatsapp.send_message("11987654321", "Teste de mensagem")

if result.get('success'):
    print("✅ Mensagem enviada!")
else:
    print(f"❌ Erro: {result.get('error')}")
```

## 📚 Documentação Completa

Consulte `WHATSAPP_GUIA.md` para documentação completa.

