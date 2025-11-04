"""
Serviço de integração com a API do Asaas
"""
import requests
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AsaasService:
    """Classe para gerenciar a comunicação com a API do Asaas"""
    
    def __init__(self):
        self.api_key = settings.ASAAS_API_KEY
        self.base_url = settings.ASAAS_API_URL
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Método auxiliar para fazer requisições à API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API do Asaas: {str(e)}")
            error_message = str(e)
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('errors', [{}])[0].get('description', str(e))
                except:
                    error_message = e.response.text or str(e)
            
            return {'success': False, 'error': error_message}
    
    # ==================== CLIENTES ====================
    
    def create_customer(self, customer_data: Dict) -> Dict:
        """
        Cria um novo cliente no Asaas
        
        Args:
            customer_data: Dicionário com os dados do cliente
        
        Returns:
            Dict com o resultado da operação
        """
        return self._make_request('POST', 'customers', customer_data)
    
    def get_customer(self, customer_id: str) -> Dict:
        """Busca um cliente pelo ID"""
        return self._make_request('GET', f'customers/{customer_id}')
    
    def update_customer(self, customer_id: str, customer_data: Dict) -> Dict:
        """Atualiza os dados de um cliente"""
        return self._make_request('PUT', f'customers/{customer_id}', customer_data)
    
    def delete_customer(self, customer_id: str) -> Dict:
        """Remove um cliente"""
        return self._make_request('DELETE', f'customers/{customer_id}')
    
    def list_customers(self, limit: int = 100, offset: int = 0) -> Dict:
        """
        Lista todos os clientes cadastrados no Asaas
        
        Args:
            limit: Número máximo de clientes por página (padrão: 100)
            offset: Número de registros a pular (paginação)
        
        Returns:
            Dict com a lista de clientes
        """
        params = {'limit': limit, 'offset': offset}
        return self._make_request('GET', 'customers', params=params)
    
    # ==================== ASSINATURAS (RECORRÊNCIAS) ====================
    
    def create_subscription(self, subscription_data: Dict) -> Dict:
        """
        Cria uma nova assinatura (recorrência) no Asaas
        
        Args:
            subscription_data: Dicionário com os dados da assinatura
        
        Returns:
            Dict com o resultado da operação
        """
        return self._make_request('POST', 'subscriptions', subscription_data)
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Busca uma assinatura pelo ID"""
        return self._make_request('GET', f'subscriptions/{subscription_id}')
    
    def update_subscription(self, subscription_id: str, subscription_data: Dict) -> Dict:
        """Atualiza os dados de uma assinatura"""
        return self._make_request('PUT', f'subscriptions/{subscription_id}', subscription_data)
    
    def delete_subscription(self, subscription_id: str) -> Dict:
        """Remove uma assinatura"""
        return self._make_request('DELETE', f'subscriptions/{subscription_id}')
    
    def list_subscriptions(self, customer_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict:
        """
        Lista assinaturas, opcionalmente filtradas por cliente
        
        Args:
            customer_id: ID do cliente (opcional)
            limit: Número máximo de assinaturas por página (padrão: 100)
            offset: Número de registros a pular (paginação)
        
        Returns:
            Dict com a lista de assinaturas
        """
        params = {'limit': limit, 'offset': offset}
        if customer_id:
            params['customer'] = customer_id
        return self._make_request('GET', 'subscriptions', params=params)
    
    # ==================== FINANCEIRO / MOVIMENTAÇÕES ====================
    
    def list_payments(self, limit: int = 100, offset: int = 0, 
                      date_from: Optional[str] = None, date_to: Optional[str] = None,
                      status: Optional[str] = None) -> Dict:
        """
        Lista os pagamentos (cobranças confirmadas)
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Deslocamento para paginação
            date_from: Data inicial (formato YYYY-MM-DD)
            date_to: Data final (formato YYYY-MM-DD)
            status: Status do pagamento (PENDING, RECEIVED, CONFIRMED, etc)
        
        Returns:
            Dict com a lista de pagamentos
        """
        params = {'limit': limit, 'offset': offset}
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if status:
            params['status'] = status
        return self._make_request('GET', 'payments', params=params)
    
    def get_financial_transactions(self, limit: int = 100, offset: int = 0,
                                   date_from: Optional[str] = None, 
                                   date_to: Optional[str] = None) -> Dict:
        """
        Lista transações financeiras (extrato detalhado)
        
        Args:
            limit: Número máximo de registros
            offset: Deslocamento para paginação
            date_from: Data inicial (formato YYYY-MM-DD)
            date_to: Data final (formato YYYY-MM-DD)
        
        Returns:
            Dict com o extrato de transações
        """
        params = {'limit': limit, 'offset': offset}
        if date_from:
            params['startDate'] = date_from
        if date_to:
            params['finishDate'] = date_to
        return self._make_request('GET', 'financialTransactions', params=params)
    
    def get_transfers(self, limit: int = 100, offset: int = 0) -> Dict:
        """
        Lista transferências realizadas
        
        Args:
            limit: Número máximo de registros
            offset: Deslocamento para paginação
        
        Returns:
            Dict com a lista de transferências
        """
        params = {'limit': limit, 'offset': offset}
        return self._make_request('GET', 'transfers', params=params)

