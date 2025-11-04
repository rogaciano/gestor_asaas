"""
Comando para popular o Plano de Contas com categorias padrão
"""
from django.core.management.base import BaseCommand
from asaas_app.models import PlanoContas


class Command(BaseCommand):
    help = 'Popula o Plano de Contas com categorias padrão'

    def handle(self, *args, **options):
        self.stdout.write('Criando Plano de Contas...')
        
        categorias = [
            # RECEITAS
            {'codigo': '1.0', 'nome': 'RECEITAS', 'tipo': 'RECEITA', 'descricao': 'Todas as receitas'},
            {'codigo': '1.1', 'nome': 'Receitas Operacionais', 'tipo': 'RECEITA', 'pai': '1.0'},
            {'codigo': '1.1.01', 'nome': 'Vendas de Produtos', 'tipo': 'RECEITA', 'pai': '1.1'},
            {'codigo': '1.1.02', 'nome': 'Prestação de Serviços', 'tipo': 'RECEITA', 'pai': '1.1'},
            {'codigo': '1.1.03', 'nome': 'Recorrências', 'tipo': 'RECEITA', 'pai': '1.1'},
            {'codigo': '1.2', 'nome': 'Receitas Financeiras', 'tipo': 'RECEITA', 'pai': '1.0'},
            {'codigo': '1.2.01', 'nome': 'Juros Recebidos', 'tipo': 'RECEITA', 'pai': '1.2'},
            {'codigo': '1.2.02', 'nome': 'Rendimentos', 'tipo': 'RECEITA', 'pai': '1.2'},
            
            # DESPESAS
            {'codigo': '2.0', 'nome': 'DESPESAS', 'tipo': 'DESPESA', 'descricao': 'Todas as despesas'},
            {'codigo': '2.1', 'nome': 'Despesas Operacionais', 'tipo': 'DESPESA', 'pai': '2.0'},
            {'codigo': '2.1.01', 'nome': 'Salários e Encargos', 'tipo': 'DESPESA', 'pai': '2.1'},
            {'codigo': '2.1.02', 'nome': 'Aluguel', 'tipo': 'DESPESA', 'pai': '2.1'},
            {'codigo': '2.1.03', 'nome': 'Energia Elétrica', 'tipo': 'DESPESA', 'pai': '2.1'},
            {'codigo': '2.1.04', 'nome': 'Internet e Telefonia', 'tipo': 'DESPESA', 'pai': '2.1'},
            {'codigo': '2.1.05', 'nome': 'Material de Escritório', 'tipo': 'DESPESA', 'pai': '2.1'},
            
            {'codigo': '2.2', 'nome': 'Despesas com Vendas', 'tipo': 'DESPESA', 'pai': '2.0'},
            {'codigo': '2.2.01', 'nome': 'Comissões', 'tipo': 'DESPESA', 'pai': '2.2'},
            {'codigo': '2.2.02', 'nome': 'Marketing e Publicidade', 'tipo': 'DESPESA', 'pai': '2.2'},
            {'codigo': '2.2.03', 'nome': 'Promoções', 'tipo': 'DESPESA', 'pai': '2.2'},
            
            {'codigo': '2.3', 'nome': 'Despesas Financeiras', 'tipo': 'DESPESA', 'pai': '2.0'},
            {'codigo': '2.3.01', 'nome': 'Taxas Bancárias', 'tipo': 'DESPESA', 'pai': '2.3'},
            {'codigo': '2.3.02', 'nome': 'Taxas Asaas', 'tipo': 'DESPESA', 'pai': '2.3'},
            {'codigo': '2.3.03', 'nome': 'Juros Pagos', 'tipo': 'DESPESA', 'pai': '2.3'},
            {'codigo': '2.3.04', 'nome': 'IOF', 'tipo': 'DESPESA', 'pai': '2.3'},
            
            {'codigo': '2.4', 'nome': 'Despesas Administrativas', 'tipo': 'DESPESA', 'pai': '2.0'},
            {'codigo': '2.4.01', 'nome': 'Contabilidade', 'tipo': 'DESPESA', 'pai': '2.4'},
            {'codigo': '2.4.02', 'nome': 'Honorários Advocatícios', 'tipo': 'DESPESA', 'pai': '2.4'},
            {'codigo': '2.4.03', 'nome': 'Softwares e Sistemas', 'tipo': 'DESPESA', 'pai': '2.4'},
            
            {'codigo': '2.5', 'nome': 'Impostos e Tributos', 'tipo': 'DESPESA', 'pai': '2.0'},
            {'codigo': '2.5.01', 'nome': 'ISS', 'tipo': 'DESPESA', 'pai': '2.5'},
            {'codigo': '2.5.02', 'nome': 'PIS/COFINS', 'tipo': 'DESPESA', 'pai': '2.5'},
            {'codigo': '2.5.03', 'nome': 'IRPJ', 'tipo': 'DESPESA', 'pai': '2.5'},
            {'codigo': '2.5.04', 'nome': 'CSLL', 'tipo': 'DESPESA', 'pai': '2.5'},
        ]
        
        created = 0
        updated = 0
        
        for cat_data in categorias:
            codigo = cat_data['codigo']
            nome = cat_data['nome']
            tipo = cat_data['tipo']
            descricao = cat_data.get('descricao', '')
            pai_codigo = cat_data.get('pai')
            
            # Busca categoria pai se existir
            categoria_pai = None
            if pai_codigo:
                try:
                    categoria_pai = PlanoContas.objects.get(codigo=pai_codigo)
                except PlanoContas.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Categoria pai {pai_codigo} não encontrada para {codigo}'))
            
            # Cria ou atualiza categoria
            categoria, created_flag = PlanoContas.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nome': nome,
                    'tipo': tipo,
                    'categoria_pai': categoria_pai,
                    'descricao': descricao,
                    'ativa': True
                }
            )
            
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Criada: {codigo} - {nome}'))
            else:
                updated += 1
                self.stdout.write(f'  Atualizada: {codigo} - {nome}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Concluído! {created} criadas, {updated} atualizadas.'))
        self.stdout.write('')
        self.stdout.write('Agora você pode:')
        self.stdout.write('  1. Importar movimentações do Asaas')
        self.stdout.write('  2. Criar regras de categorização automática')
        self.stdout.write('  3. Conciliar movimentações manualmente')

