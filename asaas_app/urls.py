from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('clientes/<int:pk>/deletar/', views.cliente_delete, name='cliente_delete'),
    path('clientes/<int:pk>/sincronizar/', views.cliente_sync, name='cliente_sync'),
    path('clientes/importar/', views.import_clientes, name='import_clientes'),
    
    # Recorrências
    path('recorrencias/', views.recorrencia_list, name='recorrencia_list'),
    path('recorrencias/nova/', views.recorrencia_create, name='recorrencia_create'),
    path('recorrencias/<int:pk>/editar/', views.recorrencia_edit, name='recorrencia_edit'),
    path('recorrencias/<int:pk>/deletar/', views.recorrencia_delete, name='recorrencia_delete'),
    path('recorrencias/<int:pk>/sincronizar/', views.recorrencia_sync, name='recorrencia_sync'),
    path('recorrencias/<int:pk>/criar-link/', views.recorrencia_criar_link, name='recorrencia_criar_link'),
    path('recorrencias/<int:pk>/boletos/', views.recorrencia_boletos, name='recorrencia_boletos'),
    path('recorrencias/<int:pk>/enviar-boleto-whatsapp/', views.recorrencia_enviar_boleto_whatsapp, name='recorrencia_enviar_boleto_whatsapp'),
    path('recorrencias/<int:pk>/enviar-link-whatsapp/', views.recorrencia_enviar_link_whatsapp, name='recorrencia_enviar_link_whatsapp'),
    path('recorrencias/importar/', views.import_recorrencias, name='import_recorrencias'),
    
    # Plano de Contas
    path('financeiro/plano-contas/', views.plano_contas_list, name='plano_contas_list'),
    path('financeiro/plano-contas/novo/', views.plano_contas_create, name='plano_contas_create'),
    path('financeiro/plano-contas/<int:pk>/editar/', views.plano_contas_edit, name='plano_contas_edit'),
    path('financeiro/plano-contas/<int:pk>/deletar/', views.plano_contas_delete, name='plano_contas_delete'),
    
    # Movimentações
    path('financeiro/movimentacoes/', views.movimentacao_list, name='movimentacao_list'),
    path('financeiro/movimentacoes/<int:pk>/editar/', views.movimentacao_edit, name='movimentacao_edit'),
    path('financeiro/movimentacoes/<int:pk>/deletar/', views.movimentacao_delete, name='movimentacao_delete'),
    path('financeiro/movimentacoes/importar/', views.import_movimentacoes, name='import_movimentacoes'),
    
    # Regras de Categorização
    path('financeiro/regras/', views.regra_list, name='regra_list'),
    path('financeiro/regras/nova/', views.regra_create, name='regra_create'),
    path('financeiro/regras/<int:pk>/editar/', views.regra_edit, name='regra_edit'),
    path('financeiro/regras/<int:pk>/deletar/', views.regra_delete, name='regra_delete'),
    path('financeiro/regras/aplicar/', views.aplicar_regras_manual, name='aplicar_regras_manual'),
    
    # Conciliação
    path('financeiro/conciliacao/', views.conciliacao, name='conciliacao'),
    path('financeiro/conciliacao/<int:pk>/rapido/', views.conciliar_rapido, name='conciliar_rapido'),
    
    # Relatórios
    path('financeiro/relatorios/', views.relatorios, name='relatorios'),
    
    # Links de Pagamento
    path('links-pagamento/', views.link_pagamento_list, name='link_pagamento_list'),
    path('links-pagamento/novo/', views.link_pagamento_create, name='link_pagamento_create'),
    path('links-pagamento/<int:pk>/editar/', views.link_pagamento_edit, name='link_pagamento_edit'),
    path('links-pagamento/<int:pk>/deletar/', views.link_pagamento_delete, name='link_pagamento_delete'),
    path('links-pagamento/<int:pk>/sincronizar/', views.link_pagamento_sync, name='link_pagamento_sync'),
    path('links-pagamento/importar/', views.import_link_pagamento, name='import_link_pagamento'),
]

