"""
Serviço de integração com API de WhatsApp
Suporta Evolution API, WhatsApp Business API e outras APIs similares
"""
import requests
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Classe para gerenciar o envio de mensagens via WhatsApp"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', '')
        self.api_key = getattr(settings, 'WHATSAPP_API_KEY', '')
        self.instance_id = getattr(settings, 'WHATSAPP_INSTANCE_ID', '')
        self.token = getattr(settings, 'WHATSAPP_TOKEN', '')
        self.provider = getattr(settings, 'WHATSAPP_PROVIDER', 'evolution').upper()
        
        # Headers baseado no provedor
        if self.provider == 'EVOLUTION':
            self.headers = {
                'apikey': self.api_key,
                'Content-Type': 'application/json'
            }
        elif self.provider == 'WHATSAPP_BUSINESS':
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        else:
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
    
    def _format_phone(self, phone: str) -> str:
        """
        Formata o número de telefone para o padrão internacional
        Remove caracteres não numéricos e adiciona código do país se necessário
        Baseado no código que funciona em outro projeto
        """
        if not phone:
            return ''
        
        # Remove caracteres não numéricos
        import re
        clean_number = re.sub(r'\D', '', phone)
        
        # Verifica tamanho mínimo
        if len(clean_number) < 10:
            return clean_number
        
        # Adiciona código do país se necessário
        if not clean_number.startswith('55'):
            clean_number = '55' + clean_number
        
        # Valida formato brasileiro (55 + DDD + número)
        # Aceita 12 ou 13 dígitos (55 + 2 dígitos DDD + 8 ou 9 dígitos)
        if len(clean_number) not in [12, 13]:
            logger.warning(f'Número formatado pode estar incorreto: {clean_number} (tamanho: {len(clean_number)})')
        
        if self.provider == 'EVOLUTION':
            return clean_number
        else:
            return f"{clean_number}@s.whatsapp.net"
    
    def check_instance_status(self) -> Dict:
        """
        Verifica o status da instância Evolution API
        
        Returns:
            Dict com o status da instância
        """
        if not self.api_url or not self.api_key:
            return {'success': False, 'error': 'WhatsApp API não configurada'}
        
        if self.provider != 'EVOLUTION':
            return {'success': False, 'error': 'Status check disponível apenas para Evolution API'}
        
        try:
            base_url = self.api_url.rstrip('/')
            url = f"{base_url}/instance/fetchInstances"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            instances = response.json()
            logger.info(f'Instâncias disponíveis: {instances}')
            
            # Procura a instância configurada
            instance_data = None
            if isinstance(instances, list):
                # Tenta por 'name' primeiro, depois 'instanceName'
                instance_data = next((
                    inst for inst in instances 
                    if inst.get('name') == self.instance_id or 
                       inst.get('instanceName') == self.instance_id or
                       inst.get('id') == self.instance_id
                ), None)
            elif isinstance(instances, dict):
                instance_data = instances.get(self.instance_id)
            
            if instance_data:
                # Evolution API retorna 'connectionStatus' não 'status'
                status = instance_data.get('connectionStatus') or instance_data.get('status', 'unknown')
                connected = status == 'open' or status == 'connected'
                
                return {
                    'success': True,
                    'status': status,
                    'instance': instance_data,
                    'connected': connected,
                    'disconnection_reason': instance_data.get('disconnectionReasonCode'),
                    'disconnection_at': instance_data.get('disconnectionAt')
                }
            else:
                return {
                    'success': False,
                    'error': f'Instância {self.instance_id} não encontrada'
                }
        except Exception as e:
            logger.error(f'Erro ao verificar status da instância: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def reconnect_instance(self) -> Dict:
        """
        Reconecta a instância Evolution API se necessário
        
        Returns:
            Dict com o resultado da reconexão
        """
        if not self.api_url or not self.api_key:
            return {'success': False, 'error': 'WhatsApp API não configurada'}
        
        if self.provider != 'EVOLUTION':
            return {'success': False, 'error': 'Reconexão disponível apenas para Evolution API'}
        
        try:
            base_url = self.api_url.rstrip('/')
            # Tenta restaurar/reconectar a instância
            url = f"{base_url}/instance/restore/{self.instance_id}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f'Reconexão iniciada para instância {self.instance_id}')
            
            return {'success': True, 'data': result}
        except Exception as e:
            logger.error(f'Erro ao reconectar instância: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def connect_instance(self) -> Dict:
        """
        Conecta a instância Evolution API
        
        Returns:
            Dict com o resultado da conexão
        """
        if not self.api_url or not self.api_key:
            return {'success': False, 'error': 'WhatsApp API não configurada'}
        
        if self.provider != 'EVOLUTION':
            return {'success': False, 'error': 'Conexão disponível apenas para Evolution API'}
        
        try:
            base_url = self.api_url.rstrip('/')
            # Tenta conectar a instância
            url = f"{base_url}/instance/connect/{self.instance_id}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f'Conexão iniciada para instância {self.instance_id}')
            
            return {'success': True, 'data': result}
        except Exception as e:
            logger.error(f'Erro ao conectar instância: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def send_message(self, phone: str, message: str) -> Dict:
        """
        Envia uma mensagem de texto via WhatsApp
        
        Args:
            phone: Número do telefone (com ou sem formatação)
            message: Mensagem a ser enviada
        
        Returns:
            Dict com o resultado da operação
        """
        if not self.api_url or not self.api_key:
            logger.warning('WhatsApp API não configurada. Verifique as variáveis WHATSAPP_API_URL e WHATSAPP_API_KEY no .env')
            return {'success': False, 'error': 'WhatsApp API não configurada'}
        
        formatted_phone = self._format_phone(phone)
        
        if not formatted_phone:
            logger.error(f'Número de telefone inválido: {phone}')
            return {'success': False, 'error': 'Número de telefone inválido'}
        
        # Se Evolution API, tenta conectar a instância antes de enviar
        # para garantir que a conexão WebSocket está ativa
        if self.provider == 'EVOLUTION':
            logger.info('Verificando conexão da instância antes de enviar...')
            connect_result = self.connect_instance()
            if connect_result.get('success'):
                logger.info('Conexão verificada/atualizada, aguardando 2 segundos...')
                import time
                time.sleep(2)  # Aguarda conexão estabilizar
        
        try:
            if self.provider == 'EVOLUTION':
                # Evolution API - formato correto sem /api
                # O endpoint usa o NOME da instância, não o ID
                base_url = self.api_url.rstrip('/')
                # Tenta usar o nome da instância (atitude) como está configurado
                url = f"{base_url}/message/sendText/{self.instance_id}"
                
                # Log detalhado para debug
                logger.info(f'URL completa: {url}')
                logger.info(f'Instance ID configurado: {self.instance_id}')
                
                data = {
                    'number': formatted_phone,
                    'text': message
                }
                
                logger.info(f'Tentando enviar via Evolution API: {url}')
                logger.info(f'Headers: {self.headers}')
                logger.info(f'Data: {data}')
            elif self.provider == 'WHATSAPP_BUSINESS':
                # WhatsApp Business API
                url = f"{self.api_url}/messages"
                data = {
                    'messaging_product': 'whatsapp',
                    'to': formatted_phone.split('@')[0],
                    'type': 'text',
                    'text': {
                        'body': message
                    }
                }
            else:
                # API genérica
                url = f"{self.api_url}/send"
                data = {
                    'phone': formatted_phone,
                    'message': message
                }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            logger.info(f'Resposta Evolution: status={response.status_code}')
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f'Mensagem WhatsApp enviada para {phone}: {message[:50]}...')
                return {'success': True, 'data': result}
            else:
                error_text = response.text
                logger.error(f'Erro ao enviar WhatsApp: {response.status_code} - {error_text}')
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', error_text)
                except:
                    error_message = error_text
                return {'success': False, 'error': error_message}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
            error_message = str(e)
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                    # Log detalhado do erro
                    logger.error(f'Resposta da API: {error_data}')
                except:
                    error_message = e.response.text or str(e)
                    logger.error(f'Resposta da API (texto): {error_message}')
            
            # Se erro 404, tenta versão alternativa da URL (com /api)
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                if self.provider == 'EVOLUTION':
                    logger.warning(f'Tentando URL alternativa com /api...')
                    base_url = self.api_url.rstrip('/')
                    if '/api' not in base_url:
                        url_alt = f"{base_url}/api/message/sendText/{self.instance_id}"
                    else:
                        url_alt = f"{base_url}/message/sendText/{self.instance_id}"
                    try:
                        response_alt = requests.post(url_alt, headers=self.headers, json=data, timeout=30)
                        response_alt.raise_for_status()
                        result = response_alt.json()
                        logger.info(f'Sucesso com URL alternativa: {url_alt}')
                        return {'success': True, 'data': result}
                    except Exception as e2:
                        logger.error(f'Erro também na URL alternativa: {str(e2)}')
            
            return {'success': False, 'error': error_message}
    
    def send_template_message(self, phone: str, template_name: str, variables: Dict) -> Dict:
        """
        Envia mensagem usando template (para APIs que suportam)
        
        Args:
            phone: Número do telefone
            template_name: Nome do template aprovado
            variables: Variáveis do template
        
        Returns:
            Dict com o resultado da operação
        """
        formatted_phone = self._format_phone(phone)
        
        try:
            if self.provider == 'EVOLUTION':
                # Evolution API com template
                url = f"{self.api_url}/message/sendTemplate/{self.instance_id}"
                data = {
                    'number': formatted_phone,
                    'template': template_name,
                    'params': variables
                }
            elif self.provider == 'WHATSAPP_BUSINESS':
                # WhatsApp Business API
                url = f"{self.api_url}/messages"
                data = {
                    'messaging_product': 'whatsapp',
                    'to': formatted_phone.split('@')[0],
                    'type': 'template',
                    'template': {
                        'name': template_name,
                        'language': {'code': 'pt_BR'},
                        'components': [
                            {
                                'type': 'body',
                                'parameters': [
                                    {'type': 'text', 'text': str(var)} for var in variables.values()
                                ]
                            }
                        ]
                    }
                }
            else:
                # Fallback para mensagem simples
                return self.send_message(phone, f"Template: {template_name}")
            
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f'Template WhatsApp enviado para {phone}: {template_name}')
            
            return {'success': True, 'data': result}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar template WhatsApp: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_test_message(self, message: str = None) -> Dict:
        """
        Envia mensagem de teste para os números configurados em WHATSAPP_NUMBERS
        
        Args:
            message: Mensagem customizada (opcional)
        
        Returns:
            Dict com o resultado da operação
        """
        test_numbers = getattr(settings, 'WHATSAPP_NUMBERS', [])
        
        if not test_numbers:
            return {'success': False, 'error': 'Nenhum número de teste configurado em WHATSAPP_NUMBERS'}
        
        test_message = message or """🔔 *Teste de Integração WhatsApp*

Esta é uma mensagem de teste enviada automaticamente pelo sistema.

✅ Sistema configurado corretamente!
✅ Evolution API conectada!

Se você recebeu esta mensagem, a integração está funcionando perfeitamente.

Atenciosamente,
Sistema de Gestão Asaas
"""
        
        results = []
        for number in test_numbers:
            number = number.strip()
            if number:
                result = self.send_message(number, test_message)
                results.append({
                    'number': number,
                    'success': result.get('success', False),
                    'error': result.get('error')
                })
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        return {
            'success': success_count > 0,
            'results': results,
            'summary': f'{success_count}/{total_count} mensagens enviadas com sucesso'
        }
    
    def send_to_test_numbers(self, message: str) -> Dict:
        """
        Envia mensagem para todos os números de teste configurados
        
        Args:
            message: Mensagem a ser enviada
        
        Returns:
            Dict com o resultado da operação
        """
        return self.send_test_message(message)

