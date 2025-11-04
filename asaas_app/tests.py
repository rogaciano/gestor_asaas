from django.test import TestCase, Client
from django.urls import reverse
from .models import Cliente, Recorrencia
from decimal import Decimal
from datetime import date, timedelta


class ClienteModelTest(TestCase):
    """Testes para o modelo Cliente"""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            name="João Silva",
            cpfCnpj="12345678901",
            email="joao@example.com",
            phone="1234567890",
            mobilePhone="11987654321"
        )
    
    def test_cliente_creation(self):
        """Testa se o cliente é criado corretamente"""
        self.assertTrue(isinstance(self.cliente, Cliente))
        self.assertEqual(self.cliente.__str__(), "João Silva - 12345678901")
    
    def test_cliente_fields(self):
        """Testa se os campos do cliente estão corretos"""
        self.assertEqual(self.cliente.name, "João Silva")
        self.assertEqual(self.cliente.cpfCnpj, "12345678901")
        self.assertEqual(self.cliente.email, "joao@example.com")
        self.assertFalse(self.cliente.synced_with_asaas)


class RecorrenciaModelTest(TestCase):
    """Testes para o modelo Recorrência"""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            name="Maria Santos",
            cpfCnpj="98765432109",
            email="maria@example.com"
        )
        
        self.recorrencia = Recorrencia.objects.create(
            cliente=self.cliente,
            value=Decimal('99.90'),
            cycle='MONTHLY',
            billing_type='BOLETO',
            description='Plano Premium',
            next_due_date=date.today() + timedelta(days=30)
        )
    
    def test_recorrencia_creation(self):
        """Testa se a recorrência é criada corretamente"""
        self.assertTrue(isinstance(self.recorrencia, Recorrencia))
        self.assertEqual(
            self.recorrencia.__str__(),
            "Plano Premium - Maria Santos - R$ 99.90"
        )
    
    def test_recorrencia_fields(self):
        """Testa se os campos da recorrência estão corretos"""
        self.assertEqual(self.recorrencia.value, Decimal('99.90'))
        self.assertEqual(self.recorrencia.cycle, 'MONTHLY')
        self.assertEqual(self.recorrencia.billing_type, 'BOLETO')
        self.assertEqual(self.recorrencia.status, 'ACTIVE')
        self.assertFalse(self.recorrencia.synced_with_asaas)


class ViewsTest(TestCase):
    """Testes para as views"""
    
    def setUp(self):
        self.client = Client()
        self.cliente = Cliente.objects.create(
            name="Pedro Oliveira",
            cpfCnpj="11122233344",
            email="pedro@example.com"
        )
    
    def test_home_view(self):
        """Testa a view da home"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_cliente_list_view(self):
        """Testa a listagem de clientes"""
        response = self.client.get(reverse('cliente_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/list.html')
        self.assertContains(response, 'Pedro Oliveira')
    
    def test_cliente_create_view_get(self):
        """Testa o acesso ao formulário de criação de cliente"""
        response = self.client.get(reverse('cliente_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/form.html')
    
    def test_recorrencia_list_view(self):
        """Testa a listagem de recorrências"""
        response = self.client.get(reverse('recorrencia_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recorrencias/list.html')


class FormTest(TestCase):
    """Testes para os formulários"""
    
    def test_cliente_form_valid(self):
        """Testa formulário de cliente válido"""
        from .forms import ClienteForm
        form_data = {
            'name': 'Ana Costa',
            'cpfCnpj': '55566677788',
            'email': 'ana@example.com',
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_cliente_form_invalid(self):
        """Testa formulário de cliente inválido"""
        from .forms import ClienteForm
        form_data = {
            'name': '',  # Nome vazio - inválido
            'cpfCnpj': '55566677788',
            'email': 'ana@example.com',
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())

