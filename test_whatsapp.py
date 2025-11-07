"""
Script para testar envio de WhatsApp
"""
from services.whatsapp_service import WhatsAppService
from datetime import datetime

print("=" * 80)
print("TESTE DE WHATSAPP - EVOLUTION API")
print("=" * 80)

# Criar serviço
ws = WhatsAppService()

# Mensagem de teste
message = f"""🧪 *Teste de Configuração WhatsApp*

✅ Token Evolution atualizado com sucesso!

📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
🔧 Sistema: Webhook Talkia

Este é um teste para confirmar que as notificações WhatsApp estão funcionando."""

# Número para teste
number = "5581999216560"

print(f"\n📱 Enviando mensagem para: {number}")
print("-" * 80)

# Enviar mensagem
result = ws.send_message(number, message)

print("-" * 80)

if result:
    print("\n✅ SUCESSO!")
    print("WhatsApp enviado com sucesso!")
    print("\n📱 Verifique seu WhatsApp para confirmar o recebimento.")
else:
    print("\n❌ FALHA!")
    print("Não foi possível enviar o WhatsApp.")
    print("\n🔍 Possíveis causas:")
    print("   1. Token Evolution incorreto")
    print("   2. Instância não conectada")
    print("   3. Número inválido")
    print("   4. Problema de conectividade")

print("\n" + "=" * 80)
