# 🔐 Primeiro Acesso ao Sistema

## Configuração Inicial de Segurança

Antes de usar o sistema, você precisa criar um usuário administrador. Siga um dos métodos abaixo:

---

## Método 1: Script Automático (Recomendado) ⭐

Criamos um script interativo que facilita a criação do primeiro usuário:

### **Windows:**
```bash
python criar_usuario.py
```

### **Linux/Mac:**
```bash
python3 criar_usuario.py
```

### **O que o script faz:**
- ✅ Solicita usuário, e-mail e senha
- ✅ Valida a força da senha automaticamente
- ✅ Cria usuário com permissões de administrador
- ✅ Mostra mensagem de sucesso com instruções

**Exemplo de uso:**
```
============================================================
CRIAR PRIMEIRO USUÁRIO - Asaas Manager
============================================================

Digite os dados do novo usuário:

Usuário: admin
E-mail (opcional): admin@exemplo.com
Senha: ********
Confirme a senha: ********

============================================================
✅ USUÁRIO CRIADO COM SUCESSO!
============================================================

Usuário: admin
E-mail: admin@exemplo.com
Tipo: Superusuário (Admin)

🔐 Você já pode fazer login no sistema!

   URL de Login: http://localhost:8000/login/

============================================================
```

---

## Método 2: Comando Django (Tradicional)

Se preferir o método tradicional do Django:

```bash
python manage.py createsuperuser
```

**Siga as instruções:**
```
Username: admin
Email: admin@exemplo.com
Password: ********
Password (again): ********
Superuser created successfully.
```

---

## 📋 Requisitos de Senha

O sistema valida automaticamente a força da senha. Requisitos:

- ✅ **Mínimo 8 caracteres**
- ✅ **Não pode ser muito similar ao usuário**
- ✅ **Não pode ser uma senha comum** (ex: password123)
- ✅ **Não pode ser totalmente numérica**

### **Exemplos de Senhas FORTES:**
```
M2@kL9#pQ7$wR4!    ✅
Xz8&Nt5%Bq2^Vy9    ✅
As@4s2025#Mgr!     ✅
```

### **Exemplos de Senhas FRACAS (evite):**
```
admin123    ❌ Muito comum
12345678    ❌ Apenas números
senha       ❌ Muito curta e comum
```

---

## 🚀 Após Criar o Usuário

### 1. **Iniciar o Servidor**

```bash
python manage.py runserver
```

### 2. **Acessar o Sistema**

Abra seu navegador e acesse:
```
http://localhost:8000/login/
```

### 3. **Fazer Login**

- Digite seu **usuário**
- Digite sua **senha**
- Clique em **Entrar**

### 4. **Pronto!**

Você será redirecionado para o dashboard do sistema! 🎉

---

## 🔒 Segurança Adicional

### **Trocar Senha**

Para trocar a senha de um usuário:

```bash
python manage.py changepassword nomedousuario
```

### **Criar Mais Usuários**

Execute o script ou comando novamente:

```bash
python criar_usuario.py
```

ou

```bash
python manage.py createsuperuser
```

### **Listar Usuários Existentes**

```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> for user in User.objects.all():
...     print(f"Usuário: {user.username}, Admin: {user.is_superuser}")
```

### **Deletar Usuário**

```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.get(username='usuario').delete()
```

---

## 🆘 Problemas Comuns

### **"Senha muito fraca"**

**Solução:** Use uma senha mais forte seguindo os requisitos acima.

### **"Usuário já existe"**

**Solução:** Use outro nome de usuário ou delete o usuário existente primeiro.

### **"ModuleNotFoundError: No module named 'django'"**

**Solução:** Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### **Esqueci minha senha**

**Solução:** Recrie o usuário:
```bash
python manage.py changepassword nomedousuario
```

---

## 📚 Próximos Passos

Após criar seu usuário e fazer login:

1. ✅ **Configure a API do Asaas** (veja [API_GUIDE.md](API_GUIDE.md))
2. ✅ **Cadastre seu primeiro cliente** (veja [QUICKSTART.md](QUICKSTART.md))
3. ✅ **Explore o sistema** (veja [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md))
4. ✅ **Prepare para produção** (veja [SEGURANCA.md](SEGURANCA.md))

---

## 🎓 Dicas de Segurança

### **Desenvolvimento:**
- Use senhas simples para facilitar testes
- Mantenha o `DEBUG=True` no `.env`

### **Produção:**
- ⚠️ **SEMPRE** use senhas fortes
- ⚠️ Configure `DEBUG=False`
- ⚠️ Siga o guia [SEGURANCA.md](SEGURANCA.md)
- ⚠️ Use HTTPS obrigatório
- ⚠️ Configure backup automático

---

**Pronto para começar!** 🚀

Se tiver dúvidas, consulte:
- [QUICKSTART.md](QUICKSTART.md) - Guia rápido de uso
- [SEGURANCA.md](SEGURANCA.md) - Guia completo de segurança
- [INDEX.md](INDEX.md) - Índice de toda documentação

