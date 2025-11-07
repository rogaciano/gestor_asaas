"""
Comando para testar o envio de WhatsApp
"""
from django.core.management.base import BaseCommand
from asaas_app.whatsapp_service import WhatsAppService


class Command(BaseCommand):
    help = 'Testa o envio de mensagens WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=str,
            help='Número de telefone para enviar (opcional, se não informado usa WHATSAPP_NUMBERS do .env)',
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Mensagem customizada (opcional)',
        )

    def handle(self, *args, **options):
        whatsapp_service = WhatsAppService()
        
        # Verifica status da instância primeiro
        self.stdout.write('Verificando status da instância...')
        status = whatsapp_service.check_instance_status()
        if status.get('success'):
            instance_status = status.get('status', 'unknown')
            connected = status.get('connected', False)
            if connected:
                self.stdout.write(self.style.SUCCESS(f'[OK] Instância conectada (status: {instance_status})'))
            else:
                self.stdout.write(self.style.WARNING(f'[AVISO] Instância NÃO conectada (status: {instance_status})'))
                self.stdout.write(self.style.WARNING('A instância precisa estar conectada para enviar mensagens.'))
        else:
            self.stdout.write(self.style.WARNING(f'[AVISO] Não foi possível verificar status: {status.get("error")}'))
        
        self.stdout.write('')
        
        number = options.get('number')
        custom_message = options.get('message')
        
        if number:
            # Envia para número específico
            self.stdout.write(f'Enviando mensagem de teste para {number}...')
            result = whatsapp_service.send_message(number, custom_message or 'Mensagem de teste do sistema Asaas Manager')
            
            if result.get('success'):
                self.stdout.write(self.style.SUCCESS(f'[OK] Mensagem enviada com sucesso para {number}!'))
            else:
                self.stdout.write(self.style.ERROR(f'[ERRO] Erro ao enviar mensagem: {result.get("error")}'))
        else:
            # Envia para todos os números configurados em WHATSAPP_NUMBERS
            self.stdout.write('Enviando mensagens de teste para números configurados...')
            result = whatsapp_service.send_test_message(custom_message)
            
            if result.get('success'):
                self.stdout.write(self.style.SUCCESS(f'✅ {result.get("summary")}'))
                
                for item in result.get('results', []):
                    if item['success']:
                        self.stdout.write(self.style.SUCCESS(f'  [OK] {item["number"]}: Enviado'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  [ERRO] {item["number"]}: {item.get("error")}'))
            else:
                self.stdout.write(self.style.ERROR(f'[ERRO] {result.get("error")}'))
                self.stdout.write(self.style.WARNING('Configure WHATSAPP_NUMBERS no .env ou use --number para testar'))

