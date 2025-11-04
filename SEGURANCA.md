# 🔐 Guia de Segurança - Asaas Manager

## Visão Geral

Este documento descreve todas as medidas de segurança implementadas no sistema e como configurá-las corretamente para produção.

---

## 🎯 Funcionalidades de Segurança Implementadas

### ✅ **1. Sistema de Autenticação**

**O que foi implementado:**
- Login obrigatório para todas as páginas
- Sistema de logout seguro
- Proteção de sessão
- Interface de login moderna e segura

**Como funciona:**
- Todas as views protegidas com `@login_required`
- Redirecionamento automático para login se não autenticado
- Sessão expira após 8 horas de inatividade
- Logout limpa completamente a sessão

### ✅ **2. Proteção CSRF**

**O que foi implementado:**
- Django CSRF middleware ativado
- Tokens CSRF em todos os formulários
- Cookies CSRF com HttpOnly

**Como funciona:**
- Cada formulário possui token CSRF único
- Protege contra ataques Cross-Site Request Forgery
- Tokens validados automaticamente pelo Django

### ✅ **3. Segurança de Sessão**

**Configurações:**
```python
SESSION_COOKIE_HTTPONLY = True      # Não acessível via JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'     # Proteção contra CSRF
SESSION_COOKIE_SECURE = True        # Apenas HTTPS (produção)
SESSION_COOKIE_AGE = 28800          # 8 horas
```

### ✅ **4. Headers de Segurança**

**Implementados:**
- **XSS Filter**: Proteção contra Cross-Site Scripting
- **Content-Type Nosniff**: Previne MIME-sniffing
- **X-Frame-Options**: Previne clickjacking (DENY)

### ✅ **5. HTTPS/SSL (Produção)**

**Configurações para produção:**
- SSL Redirect: Força HTTPS
- HSTS: HTTP Strict Transport Security
- Secure Cookies: Apenas HTTPS

### ✅ **6. Logging de Segurança**

**Sistema de logs:**
- Logs de segurança em `logs/security.log`
- Registro de tentativas de login falhas
- Erros de API registrados
- Logs de console para debug

---

## 🚀 Configuração para Produção

### 1. **Criar Primeiro Usuário**

Antes de qualquer coisa, crie um usuário administrador:

```bash
python manage.py createsuperuser
```

Siga as instruções:
```
Username: admin
Email: seu@email.com
Password: ********
Password (again): ********
```

**⚠️ IMPORTANTE:**
- Use senha forte (mínimo 8 caracteres)
- Combine letras maiúsculas, minúsculas, números e símbolos
- Não use senhas óbvias como "admin123"

### 2. **Configurar Variáveis de Ambiente**

Edite o arquivo `.env` com as configurações de produção:

```env
# Django
SECRET_KEY=sua-chave-secreta-unica-aqui-gere-uma-nova
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Asaas API
ASAAS_API_KEY=sua-chave-de-producao
ASAAS_API_URL=https://api.asaas.com/v3

# Security (HTTPS)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 3. **Gerar SECRET_KEY Segura**

Execute no terminal Python:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Ou use este comando:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copie a chave gerada e coloque no `.env`

### 4. **Configurar ALLOWED_HOSTS**

Liste todos os domínios que acessarão o sistema:

```env
ALLOWED_HOSTS=meusite.com,www.meusite.com,api.meusite.com
```

**Nunca use `*` em produção!**

### 5. **Verificar Configurações de Segurança**

Execute o comando de verificação do Django:

```bash
python manage.py check --deploy
```

Este comando mostra avisos e erros de configuração de segurança.

---

## 🔒 Boas Práticas de Segurança

### **1. Senhas**

**Recomendações:**
- ✅ Mínimo 12 caracteres
- ✅ Misture maiúsculas, minúsculas, números e símbolos
- ✅ Não use palavras do dicionário
- ✅ Não reutilize senhas
- ✅ Troque senhas periodicamente (a cada 90 dias)

**Exemplos de senhas FORTES:**
```
M2@kL9#pQ7$wR4!
Xz8&Nt5%Bq2^Vy9
```

**Exemplos de senhas FRACAS (NÃO USE):**
```
admin123
senha123
asaas2025
```

### **2. API Key do Asaas**

**Segurança:**
- ✅ Nunca commite a API Key no Git
- ✅ Sempre use arquivo `.env`
- ✅ Gere chaves diferentes para dev e produção
- ✅ Rotacione as chaves periodicamente
- ✅ Monitore uso da API no painel do Asaas

**Como proteger:**
```bash
# Verifique se o .env está no .gitignore
cat .gitignore | grep .env

# Deve aparecer:
.env
*.env
```

### **3. Banco de Dados**

**Produção:**
- ✅ Use PostgreSQL, não SQLite
- ✅ Backup automático diário
- ✅ Senha forte do banco
- ✅ Acesso restrito ao servidor do banco
- ✅ Criptografia em trânsito (SSL)

**Exemplo de configuração:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'asaas_db',
        'USER': 'asaas_user',
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',  # SSL obrigatório
        }
    }
}
```

### **4. Servidor Web**

**Configuração Nginx:**
```nginx
# Force HTTPS
server {
    listen 80;
    server_name seudominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name seudominio.com;
    
    # SSL Certificates
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # ... resto da configuração
}
```

### **5. Firewall**

**Configure UFW (Ubuntu):**

```bash
# Permitir apenas portas necessárias
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Verificar status
sudo ufw status
```

### **6. Atualizações**

**Mantenha tudo atualizado:**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Atualizar dependências Python
pip install --upgrade -r requirements.txt

# Verificar vulnerabilidades
pip install safety
safety check
```

---

## 🛡️ Proteções Contra Ataques Comuns

### **1. SQL Injection**

**✅ PROTEGIDO**
- Django ORM previne automaticamente
- Nunca use queries SQL diretas sem sanitização

**Correto:**
```python
Cliente.objects.filter(name=user_input)  # ✅ Seguro
```

**Incorreto:**
```python
cursor.execute(f"SELECT * FROM clientes WHERE name = '{user_input}'")  # ❌ PERIGOSO!
```

### **2. Cross-Site Scripting (XSS)**

**✅ PROTEGIDO**
- Django escapa automaticamente HTML nos templates
- XSS Filter ativado

**Templates escapam automaticamente:**
```html
{{ cliente.name }}  <!-- Automaticamente escapado -->
```

### **3. Cross-Site Request Forgery (CSRF)**

**✅ PROTEGIDO**
- Tokens CSRF em todos os formulários
- Middleware CSRF ativado

**Sempre use em formulários:**
```html
<form method="post">
    {% csrf_token %}  <!-- OBRIGATÓRIO -->
    ...
</form>
```

### **4. Clickjacking**

**✅ PROTEGIDO**
- X-Frame-Options: DENY
- Não permite embedding em iframes

### **5. Brute Force (Login)**

**Proteções recomendadas:**

1. **Rate Limiting** (adicionar):
```bash
pip install django-ratelimit
```

2. **Django Axes** (tentativas de login):
```bash
pip install django-axes
```

3. **Captcha** (após N tentativas):
```bash
pip install django-recaptcha
```

---

## 📊 Monitoramento de Segurança

### **1. Logs**

**Verificar logs regularmente:**

```bash
# Ver últimos erros de segurança
tail -f logs/security.log

# Buscar tentativas de login falhas
grep "Failed login" logs/security.log

# Contar tentativas por IP
grep "Failed login" logs/security.log | cut -d' ' -f5 | sort | uniq -c | sort -rn
```

### **2. Alertas**

**Configure alertas para:**
- Múltiplas tentativas de login falhas
- Acesso de IPs suspeitos
- Erros 500 frequentes
- Uso anormal da API

### **3. Backups**

**Estratégia de backup:**

```bash
# Backup diário do banco
0 2 * * * pg_dump asaas_db > /backup/asaas_$(date +\%Y\%m\%d).sql

# Backup semanal dos arquivos
0 3 * * 0 tar -czf /backup/asaas_files_$(date +\%Y\%m\%d).tar.gz /var/www/asaas

# Manter backups por 30 dias
find /backup -type f -mtime +30 -delete
```

---

## 🚨 Checklist de Segurança para Deploy

### Antes do Deploy:

- [ ] `DEBUG=False` no `.env`
- [ ] `SECRET_KEY` única gerada
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] API Key de **produção** do Asaas
- [ ] Usuário admin criado com senha forte
- [ ] Certificado SSL instalado
- [ ] Configurações HTTPS ativadas
- [ ] Firewall configurado
- [ ] Backups automáticos configurados

### Após o Deploy:

- [ ] Testar login/logout
- [ ] Verificar HTTPS funcionando
- [ ] Testar todas as funcionalidades
- [ ] Verificar logs
- [ ] Monitorar performance
- [ ] Configurar monitoramento de uptime

---

## 🆘 Em Caso de Incidente de Segurança

### **1. Identificação**

Se suspeitar de acesso não autorizado:

1. **Verificar logs imediatamente:**
```bash
tail -100 logs/security.log
```

2. **Verificar sessões ativas:**
```bash
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().delete()  # Invalida todas as sessões
```

### **2. Contenção**

**Ações imediatas:**

1. Trocar todas as senhas:
```bash
python manage.py changepassword admin
```

2. Revogar API Keys comprometidas:
   - Acesse painel do Asaas
   - Gere nova API Key
   - Atualize no `.env`
   - Restart do servidor

3. Verificar dados:
```bash
# Verificar últimas modificações
python manage.py shell
>>> from asaas_app.models import Cliente, Recorrencia
>>> Cliente.objects.order_by('-updated_at')[:10]
```

### **3. Recuperação**

1. Restaurar de backup se necessário
2. Atualizar sistema e dependências
3. Revisar configurações de segurança
4. Documentar o incidente

### **4. Prevenção**

1. Investigar como aconteceu
2. Implementar medidas preventivas
3. Treinar equipe
4. Melhorar monitoramento

---

## 📞 Contatos de Segurança

### **Reportar Vulnerabilidades**

Se encontrar uma vulnerabilidade de segurança:

1. **NÃO divulgue publicamente**
2. Entre em contato imediatamente
3. Forneça detalhes técnicos
4. Aguarde correção antes de divulgar

### **Recursos Externos**

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Django Security**: https://docs.djangoproject.com/en/4.2/topics/security/
- **Asaas Security**: suporte@asaas.com

---

## ✅ Resumo das Configurações

### **Desenvolvimento:**
```env
DEBUG=True
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
ASAAS_API_URL=https://sandbox.asaas.com/api/v3
```

### **Produção:**
```env
DEBUG=False
SECRET_KEY=chave-unica-gerada
ALLOWED_HOSTS=seudominio.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
ASAAS_API_URL=https://api.asaas.com/v3
```

---

**Sistema protegido e pronto para produção!** 🔐

Para mais informações sobre deploy, consulte [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md).

