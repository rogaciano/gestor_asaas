# 🚀 Guia Rápido de Início

## Configuração Rápida (5 minutos)

### Passo 1: Execute o script de setup

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Passo 2: Configure sua API Key do Asaas

Edite o arquivo `.env` e adicione sua chave de API:

```
ASAAS_API_KEY=sua-chave-aqui
```

**Como obter sua API Key:**
1. Acesse https://www.asaas.com
2. Faça login na sua conta
3. Vá em "Integrações" > "API Key"
4. Copie sua chave

**Ambiente Sandbox (testes):**
- Use: `ASAAS_API_URL=https://sandbox.asaas.com/api/v3`
- Crie uma conta sandbox em: https://sandbox.asaas.com

### Passo 3: Inicie o servidor

**Windows:**
```bash
venv\Scripts\activate
python manage.py runserver
```

**Linux/Mac:**
```bash
source venv/bin/activate
python manage.py runserver
```

### Passo 4: Acesse o sistema

Abra seu navegador em: http://localhost:8000

## 📝 Primeiro Uso

### 1. Cadastre um Cliente
1. Clique em "Clientes" no menu
2. Clique em "Novo Cliente"
3. Preencha os dados (CPF/CNPJ, Nome, Email são obrigatórios)
4. Clique em "Salvar"
5. ✅ Cliente será automaticamente sincronizado com o Asaas!

### 2. Crie uma Recorrência
1. Clique em "Recorrências" no menu
2. Clique em "Nova Recorrência"
3. Selecione o cliente cadastrado
4. Configure:
   - Descrição (ex: "Plano Mensal Premium")
   - Valor (ex: 99.90)
   - Ciclo (ex: Mensal)
   - Forma de pagamento (ex: Boleto)
   - Data do próximo vencimento
5. Clique em "Salvar"
6. ✅ Recorrência criada e sincronizada!

## 🎯 Comandos Úteis

### Criar superusuário (acesso ao admin)
```bash
python manage.py createsuperuser
```

Acesse: http://localhost:8000/admin

### Resetar banco de dados
```bash
python manage.py flush
```

### Criar novas migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🔧 Troubleshooting

### Erro: "No module named django"
```bash
# Certifique-se de que o ambiente virtual está ativado
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro de sincronização com Asaas
- ✅ Verifique se a API Key está correta no `.env`
- ✅ Confirme se está usando a URL correta (sandbox vs produção)
- ✅ Verifique se tem saldo/créditos na conta Asaas

### Cliente não sincroniza
- ✅ CPF/CNPJ deve ser válido
- ✅ Email deve ser único
- ✅ Verifique os logs no terminal

## 📚 Próximos Passos

1. ✅ Explore o dashboard
2. ✅ Cadastre mais clientes
3. ✅ Crie diferentes tipos de recorrências
4. ✅ Teste os diferentes ciclos de cobrança
5. ✅ Acesse o admin do Django

## 💡 Dicas

- **Ambiente Sandbox:** Use para testes sem cobranças reais
- **CPF de Teste:** Use geradores online para CPFs válidos de teste
- **Backup:** O banco SQLite fica em `db.sqlite3`
- **Logs:** Verifique o terminal para mensagens de erro detalhadas

## 🆘 Precisa de Ajuda?

- 📖 Leia o [README.md](README.md) completo
- 🌐 Documentação do Asaas: https://docs.asaas.com
- 📧 Suporte Asaas: suporte@asaas.com

---

Pronto! Você está pronto para usar o Asaas Manager! 🎉

