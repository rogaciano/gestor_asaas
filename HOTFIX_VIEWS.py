# HOTFIX TEMPORÁRIO - Cole no início de views.py se whatsapp_service não existir na VPS

# Comente a linha:
# from .whatsapp_service import WhatsAppService

# E adicione esta classe temporária antes das views:
class WhatsAppService:
    """Classe temporária para evitar erro de importação"""
    def __init__(self):
        pass
    
    def send_message(self, phone, message):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'WhatsApp desabilitado temporariamente. Mensagem não enviada para {phone}')
        return {'success': False, 'error': 'WhatsApp não configurado'}
