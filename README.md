# Asaas Manager - Sistema de Gestão de Clientes e Recorrências

Sistema desenvolvido em Django para gerenciamento de clientes e recorrências (assinaturas) integrado com a API do Asaas.

## 🚀 Características

- ✅ Cadastro completo de clientes com dados pessoais e endereço
- ✅ Gerenciamento de recorrências (assinaturas)
- ✅ Sincronização automática com API do Asaas
- ✅ Interface moderna com Tailwind CSS
- ✅ Interatividade com Alpine.js
- ✅ Dashboard com estatísticas
- ✅ Máscaras de entrada para CPF/CNPJ, telefone e CEP
- ✅ Sistema de mensagens de feedback

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta no Asaas (https://www.asaas.com)
- API Key do Asaas

## 🔧 Instalação

### 1. Clone o repositório ou navegue até a pasta do projeto

```bash
cd cadastro_asaas
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (você pode copiar o `.env.example`):

```bash
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ASAAS_API_KEY=sua-api-key-do-asaas
ASAAS_API_URL=https://sandbox.asaas.com/api/v3
```

**Importante:** 
- Para ambiente de produção, use: `https://api.asaas.com/v3`
- Para ambiente de testes (sandbox), use: `https://sandbox.asaas.com/api/v3`
- Obtenha sua API Key em: https://www.asaas.com/api/v3/apiKey

### 6. Execute as migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. (Opcional) Crie um superusuário para acessar o admin

```bash
python manage.py createsuperuser
```

### 8. Inicie o servidor

```bash
python manage.py runserver
```

Acesse o sistema em: http://localhost:8000

## 📱 Uso

### Dashboard
- Acesse a página inicial para ver estatísticas do sistema
- Total de clientes cadastrados
- Total de recorrências
- Recorrências ativas
- Clientes sincronizados com Asaas

### Clientes
1. **Cadastrar Cliente:** Clique em "Novo Cliente" e preencha o formulário
2. **Editar Cliente:** Na lista de clientes, clique em "Editar"
3. **Sincronizar:** Sincronize manualmente um cliente com o Asaas
4. **Excluir:** Remove o cliente do sistema e do Asaas (se sincronizado)

### Recorrências
1. **Criar Recorrência:** Selecione um cliente sincronizado e configure a assinatura
2. **Ciclos disponíveis:** Semanal, Quinzenal, Mensal, Trimestral, Semestral, Anual
3. **Formas de pagamento:** Boleto, Cartão de Crédito, PIX
4. **Editar/Excluir:** Gerencie recorrências existentes

## 🎨 Tecnologias Utilizadas

- **Backend:** Django 4.2.7
- **Frontend:** Tailwind CSS 3.x
- **JavaScript:** Alpine.js 3.x
- **API:** Asaas API v3
- **Database:** SQLite (pode ser alterado para PostgreSQL/MySQL)

## 📁 Estrutura do Projeto

```
cadastro_asaas/
│
├── config/                 # Configurações do Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── asaas_app/             # Aplicação principal
│   ├── models.py          # Models Cliente e Recorrencia
│   ├── views.py           # Views do sistema
│   ├── forms.py           # Formulários
│   ├── services.py        # Integração com API Asaas
│   ├── urls.py            # URLs da aplicação
│   └── admin.py           # Configuração do admin
│
├── templates/             # Templates HTML
│   ├── base.html
│   ├── home.html
│   ├── clientes/
│   └── recorrencias/
│
├── requirements.txt       # Dependências Python
├── manage.py             # Script de gerenciamento Django
├── .env.example          # Exemplo de variáveis de ambiente
└── README.md             # Este arquivo
```

## 🔐 Segurança

- Nunca commite o arquivo `.env` com suas credenciais
- Use a chave da API do Asaas com cuidado
- Em produção, configure `DEBUG=False` no `.env`
- Use HTTPS em produção

## 📚 API do Asaas

Este sistema utiliza os seguintes endpoints da API do Asaas:

- **Clientes:** `/customers` (GET, POST, PUT, DELETE)
- **Assinaturas:** `/subscriptions` (GET, POST, PUT, DELETE)

Documentação completa: https://docs.asaas.com/

## 🐛 Problemas Comuns

### Erro de sincronização com Asaas
- Verifique se sua API Key está correta
- Confirme se está usando a URL correta (sandbox vs produção)
- Verifique os logs do Django para detalhes do erro

### Cliente não sincroniza
- Certifique-se de que todos os campos obrigatórios estão preenchidos
- CPF/CNPJ deve ser válido
- E-mail deve ser único na base do Asaas

### Recorrência não é criada
- O cliente precisa estar sincronizado com o Asaas primeiro
- Verifique se a data de vencimento é futura
- Confirme se o valor é maior que zero

## 🤝 Contribuindo

Sinta-se à vontade para contribuir com melhorias:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível para uso livre.

## 👨‍💻 Autor

Desenvolvido com ❤️ para facilitar a gestão de clientes e recorrências no Asaas.

## 📞 Suporte

Para dúvidas sobre a API do Asaas:
- Documentação: https://docs.asaas.com/
- Suporte: suporte@asaas.com

---

**Nota:** Este é um sistema de gerenciamento. Sempre teste em ambiente sandbox antes de usar em produção!

