# 🔍 Diagnóstico: Login Não Autentica no Servidor

## 🚨 Problema

No servidor, o login não autentica - você digita usuário e senha, mas não consegue entrar.

## 🔧 Diagnóstico Rápido

Execute estes comandos no servidor para identificar o problema:

### 1. Verificar Configurações do .env

```bash
cd /var/www/gestor_asaas
cat .env | grep -E "DEBUG|SESSION_COOKIE|CSRF|ALLOWED_HOSTS|FORCE_SCRIPT"
```

**Verifique:**
- `DEBUG=False` (em produção)
- `SESSION_COOKIE_SECURE=False` (se não tiver HTTPS)
- `CSRF_COOKIE_SECURE=False` (se não tiver HTTPS)
- `ALLOWED_HOSTS` deve ter o IP/domínio do servidor
- `CSRF_TRUSTED_ORIGINS` deve ter o IP/domínio do servidor

### 2. Verificar Logs de Erro

```bash
# Logs do Django
tail -50 logs/security.log

# Logs do servidor web (Nginx)
tail -50 /var/log/nginx/error.log

# Logs do Gunicorn (se usar)
journalctl -u gunicorn -n 50
```

### 3. Testar Autenticação Manualmente

```bash
cd /var/www/gestor_asaas
source venv/bin/activate
python manage.py shell
```

No shell do Django:
```python
from django.contrib.auth import authenticate
user = authenticate(username='seu_usuario', password='sua_senha')
print(user)  # Deve mostrar o objeto User, não None
```

## ✅ Soluções Mais Comuns

### Problema 1: SESSION_COOKIE_SECURE=True sem HTTPS

**Sintoma:** Cookies não são salvos porque o navegador bloqueia cookies "Secure" em HTTP.

**Solução:**

Edite o `.env` no servidor:
```bash
nano .env
```

Altere:
```env
# Se NÃO tiver HTTPS, use False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

Reinicie o servidor:
```bash
sudo systemctl restart gunicorn
# ou
sudo systemctl restart apache2
```

### Problema 2: CSRF_TRUSTED_ORIGINS não configurado

**Sintoma:** Erro 403 Forbidden ao fazer login.

**Solução:**

Edite o `.env`:
```bash
nano .env
```

Adicione (substitua pelo IP/domínio do seu servidor):
```env
CSRF_TRUSTED_ORIGINS=http://SEU_IP,http://SEU_DOMINIO
ALLOWED_HOSTS=SEU_IP,SEU_DOMINIO,localhost,127.0.0.1
```

Exemplo:
```env
CSRF_TRUSTED_ORIGINS=http://192.168.1.100,http://meuservidor.com
ALLOWED_HOSTS=192.168.1.100,meuservidor.com,localhost,127.0.0.1
```

Reinicie o servidor.

### Problema 3: Cookies não funcionam (path errado)

**Sintoma:** Login parece funcionar mas não mantém a sessão.

**Solução:**

Se estiver usando subdiretório (ex: `/gestor_asaas/`), verifique o `.env`:
```env
FORCE_SCRIPT_NAME=/gestor_asaas
```

E verifique se o `settings.py` está configurando os paths corretamente (já deve estar).

### Problema 4: Banco de dados não tem usuários

**Sintoma:** Nenhum usuário consegue fazer login.

**Solução:**

Crie um superusuário:
```bash
cd /var/www/gestor_asaas
source venv/bin/activate
python manage.py createsuperuser
```

Ou use o script:
```bash
python criar_usuario.py
```

### Problema 5: Migrações não aplicadas

**Sintoma:** Erro ao autenticar, tabelas não existem.

**Solução:**

```bash
cd /var/www/gestor_asaas
source venv/bin/activate
python manage.py migrate
```

## 🔧 Correção Rápida (Script)

Crie um script `corrigir_login.sh` no servidor:

```bash
#!/bin/bash
cd /var/www/gestor_asaas

echo "🔧 Corrigindo configurações de login..."

# Backup do .env
cp .env .env.backup

# Edita .env para corrigir problemas comuns
sed -i 's/SESSION_COOKIE_SECURE=True/SESSION_COOKIE_SECURE=False/g' .env
sed -i 's/CSRF_COOKIE_SECURE=True/CSRF_COOKIE_SECURE=False/g' .env

# Adiciona CSRF_TRUSTED_ORIGINS se não existir
if ! grep -q "CSRF_TRUSTED_ORIGINS" .env; then
    echo "" >> .env
    echo "# CSRF Trusted Origins" >> .env
    echo "CSRF_TRUSTED_ORIGINS=http://$(hostname -I | awk '{print $1}')" >> .env
fi

# Adiciona ALLOWED_HOSTS se não existir
if ! grep -q "ALLOWED_HOSTS" .env; then
    echo "" >> .env
    echo "# Allowed Hosts" >> .env
    echo "ALLOWED_HOSTS=$(hostname -I | awk '{print $1}'),localhost,127.0.0.1" >> .env
fi

echo "✅ Configurações atualizadas!"
echo "🔄 Reiniciando servidor..."

# Reinicia o servidor (ajuste conforme seu setup)
sudo systemctl restart gunicorn || sudo systemctl restart apache2

echo "✅ Pronto! Teste o login novamente."
```

Torne executável e execute:
```bash
chmod +x corrigir_login.sh
./corrigir_login.sh
```

## 📋 Checklist de Verificação

Execute este checklist no servidor:

```bash
cd /var/www/gestor_asaas

echo "=== Verificando .env ==="
grep -E "DEBUG|SESSION_COOKIE|CSRF|ALLOWED" .env

echo ""
echo "=== Verificando banco de dados ==="
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Usuários: {User.objects.count()}')"

echo ""
echo "=== Verificando migrações ==="
python manage.py showmigrations | grep "\[ \]"

echo ""
echo "=== Verificando logs ==="
tail -5 logs/security.log
```

## 🧪 Teste Final

Após corrigir, teste:

1. **Limpe os cookies do navegador** (F12 > Application > Clear storage)
2. Acesse a página de login
3. Digite usuário e senha
4. Clique em "Entrar"
5. Deve redirecionar para a home

Se ainda não funcionar, verifique os logs em tempo real:

```bash
# Terminal 1: Logs do Django
tail -f logs/security.log

# Terminal 2: Logs do servidor web
tail -f /var/log/nginx/error.log
```

Faça o login e observe os erros nos logs.

## 🆘 Se Nada Funcionar

1. **Verifique se o usuário existe:**
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
```

2. **Teste autenticação direta:**
```bash
python manage.py shell
>>> from django.contrib.auth import authenticate
>>> user = authenticate(username='admin', password='sua_senha')
>>> print(user)
```

3. **Verifique permissões do banco:**
```bash
python manage.py dbshell
# No PostgreSQL:
\dt django_session
SELECT * FROM django_session LIMIT 5;
```

4. **Limpe sessões antigas:**
```bash
python manage.py clearsessions
```

---

**Importante:** Sempre faça backup do `.env` antes de modificar!

```bash
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

