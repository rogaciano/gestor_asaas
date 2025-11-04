# 🚀 Checklist de Deploy para Produção

## 📋 Pré-Deploy

### 1. Ambiente de Desenvolvimento ✅
- [x] Sistema funcionando localmente
- [x] Todos os testes passando
- [x] Sem erros de linter
- [x] Documentação completa

### 2. Configurações de Segurança 🔒

#### Arquivo .env
```bash
# IMPORTANTE: Alterar para produção!
SECRET_KEY=gere-uma-nova-chave-secreta-forte
DEBUG=False  # MUITO IMPORTANTE!
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# API Asaas PRODUÇÃO
ASAAS_API_KEY=sua-api-key-de-producao
ASAAS_API_URL=https://api.asaas.com/v3

# Database
DATABASE_URL=postgres://user:pass@localhost/dbname
```

#### Gerar SECRET_KEY
```python
# Execute no terminal:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Banco de Dados 🗄️

#### PostgreSQL (Recomendado)
```bash
# Instalar psycopg2
pip install psycopg2-binary

# Adicionar ao requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
```

#### Configurar settings.py
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
```

### 4. Arquivos Estáticos 📦

#### Configurar settings.py
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Whitenoise para servir arquivos estáticos
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Adicionar
    # ... resto
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### Instalar Whitenoise
```bash
pip install whitenoise
```

## 🔧 Configurações de Servidor

### 1. Instalar Dependências do Sistema

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx
```

### 2. Criar Ambiente Virtual
```bash
cd /var/www/cadastro_asaas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Gunicorn

#### Instalar
```bash
pip install gunicorn
```

#### Criar arquivo gunicorn.service
```ini
[Unit]
Description=Gunicorn for Asaas Manager
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cadastro_asaas
Environment="PATH=/var/www/cadastro_asaas/venv/bin"
ExecStart=/var/www/cadastro_asaas/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/cadastro_asaas/gunicorn.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4. Configurar Nginx

#### Criar arquivo nginx config
```nginx
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;

    location /static/ {
        alias /var/www/cadastro_asaas/staticfiles/;
    }

    location / {
        proxy_pass http://unix:/var/www/cadastro_asaas/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. SSL com Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com -d www.seudominio.com
```

## 📝 Checklist de Deploy

### Antes do Deploy
- [ ] Alterar DEBUG=False no .env
- [ ] Gerar nova SECRET_KEY
- [ ] Configurar ALLOWED_HOSTS
- [ ] Usar API Key de PRODUÇÃO do Asaas
- [ ] Configurar banco de dados PostgreSQL
- [ ] Backup do banco de dados local (se houver dados importantes)
- [ ] Testar tudo em ambiente de staging

### Durante o Deploy
- [ ] Fazer upload dos arquivos
- [ ] Criar ambiente virtual
- [ ] Instalar dependências
- [ ] Configurar variáveis de ambiente
- [ ] Executar migrações: `python manage.py migrate`
- [ ] Coletar arquivos estáticos: `python manage.py collectstatic`
- [ ] Criar superusuário: `python manage.py createsuperuser`
- [ ] Configurar Gunicorn
- [ ] Configurar Nginx
- [ ] Configurar SSL
- [ ] Iniciar serviços

### Após o Deploy
- [ ] Testar acesso ao site
- [ ] Testar cadastro de cliente
- [ ] Testar criação de recorrência
- [ ] Verificar sincronização com Asaas
- [ ] Testar em diferentes navegadores
- [ ] Testar em mobile
- [ ] Configurar monitoramento
- [ ] Configurar backup automático
- [ ] Documentar credenciais de acesso

## 🔍 Verificações de Segurança

### Settings.py - Produção
```python
# Segurança
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## 📊 Monitoramento

### Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Sentry (Opcional)
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

## 🔄 Backup

### Backup do Banco de Dados
```bash
# PostgreSQL
pg_dump -U usuario -d nome_banco > backup_$(date +%Y%m%d).sql

# Restaurar
psql -U usuario -d nome_banco < backup_20250101.sql
```

### Backup dos Arquivos
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz /var/www/cadastro_asaas
```

## 🚨 Troubleshooting Produção

### Erro 502 Bad Gateway
```bash
# Verificar Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Reiniciar
sudo systemctl restart gunicorn
```

### Erro 500 Internal Server Error
```bash
# Ver logs do Django
tail -f /var/www/cadastro_asaas/logs/django.log

# Verificar DEBUG=False
# Verificar ALLOWED_HOSTS
```

### Problemas com Arquivos Estáticos
```bash
# Recoletar
python manage.py collectstatic --clear --noinput

# Verificar permissões
sudo chown -R www-data:www-data /var/www/cadastro_asaas/staticfiles
```

## 📱 Deploy Alternativo: Heroku

### Passo a Passo

1. **Instalar Heroku CLI**
```bash
# Windows: baixe do site
# Linux: 
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Criar arquivos necessários**

**Procfile:**
```
web: gunicorn config.wsgi
```

**runtime.txt:**
```
python-3.11.5
```

3. **Deploy**
```bash
heroku login
heroku create nome-do-app
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

4. **Configurar variáveis**
```bash
heroku config:set SECRET_KEY=sua-chave
heroku config:set DEBUG=False
heroku config:set ASAAS_API_KEY=sua-key
heroku config:set ASAAS_API_URL=https://api.asaas.com/v3
```

## 🎯 Deploy VPS (DigitalOcean, AWS, etc)

### Passos Resumidos
1. Criar Droplet/Instância
2. SSH no servidor
3. Instalar dependências
4. Clonar/Upload código
5. Configurar ambiente virtual
6. Configurar .env
7. Executar migrações
8. Configurar Gunicorn
9. Configurar Nginx
10. Configurar SSL
11. Testar

## ✅ Checklist Final

### Antes de Colocar no Ar
- [ ] Todos os testes passando
- [ ] Debug=False
- [ ] API Key de produção configurada
- [ ] SSL configurado
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Documentação atualizada

### Primeiro Acesso Produção
- [ ] Criar superusuário
- [ ] Testar login admin
- [ ] Cadastrar cliente teste
- [ ] Criar recorrência teste
- [ ] Verificar no Asaas se apareceu
- [ ] Testar edição
- [ ] Testar exclusão

---

**Pronto para produção!** 🚀

Lembre-se:
- ⚠️ Sempre teste em staging antes
- 💾 Faça backup antes de qualquer alteração
- 📊 Monitor logs regularmente
- 🔐 Mantenha credenciais seguras

