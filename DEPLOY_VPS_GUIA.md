# 🚀 Guia Completo de Deploy na VPS

## Pré-requisitos

- VPS com Ubuntu 20.04+ ou Debian 10+
- Acesso root (sudo)
- Domínio apontando para o IP da VPS
- Arquivos do projeto na VPS

---

## Método 1: Deploy Automático (Recomendado) ⭐

### **Passo 1: Tornar o script executável**

```bash
chmod +x deploy_vps.sh
```

### **Passo 2: Executar o script**

```bash
sudo bash deploy_vps.sh
```

### **Passo 3: Responder as perguntas**

O script vai pedir:
- Nome do banco de dados
- Usuário do banco
- Senha do banco (ou gera automaticamente)
- Domínio da VPS
- API Key do Asaas

### **Passo 4: Criar usuário admin**

Durante o processo, você será solicitado a criar um superusuário:
- Username
- Email
- Password

**Pronto!** O script faz tudo automaticamente! 🎉

---

## Método 2: Deploy Manual

Se preferir fazer passo a passo manualmente:

### **1. Atualizar Sistema**

```bash
sudo apt update
sudo apt upgrade -y
```

### **2. Instalar Dependências**

```bash
# Python e ferramentas
sudo apt install -y python3 python3-pip python3-venv python3-dev

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Nginx
sudo apt install -y nginx

# Certbot (SSL)
sudo apt install -y certbot python3-certbot-nginx

# Outras ferramentas
sudo apt install -y git curl
```

### **3. Configurar PostgreSQL**

```bash
# Entrar no PostgreSQL
sudo -u postgres psql

# Criar banco e usuário (substitua os valores)
CREATE DATABASE asaas_db;
CREATE USER asaas_user WITH PASSWORD 'sua_senha_forte_aqui';
ALTER ROLE asaas_user SET client_encoding TO 'utf8';
ALTER ROLE asaas_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asaas_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE asaas_db TO asaas_user;
\q
```

### **4. Configurar Ambiente Virtual**

```bash
# Ir para o diretório do projeto
cd /caminho/do/projeto

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### **5. Configurar settings.py para PostgreSQL**

Edite `config/settings.py`:

```python
# Adicione após as outras configurações de banco

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='asaas_db'),
            'USER': config('DB_USER', default='asaas_user'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
    
    # Static files em produção
    STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### **6. Configurar .env para Produção**

```bash
# Gerar SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Criar arquivo .env
nano .env
```

Conteúdo do `.env`:

```env
# Django
SECRET_KEY=cole-a-chave-gerada-aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Database
DB_NAME=asaas_db
DB_USER=asaas_user
DB_PASSWORD=sua_senha_do_banco
DB_HOST=localhost
DB_PORT=5432

# Asaas API
ASAAS_API_KEY=sua_chave_de_producao
ASAAS_API_URL=https://api.asaas.com/v3

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### **7. Executar Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **8. Coletar Arquivos Estáticos**

```bash
python manage.py collectstatic --noinput
```

### **9. Criar Superusuário**

```bash
python manage.py createsuperuser
```

### **10. Testar com Servidor de Desenvolvimento**

```bash
python manage.py runserver 0.0.0.0:8000
```

Acesse: `http://IP_DA_VPS:8000/login/`

Se funcionar, pode continuar!

### **11. Configurar Gunicorn**

**Criar arquivo de socket:**

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

**Criar arquivo de serviço:**

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=seu_usuario
Group=www-data
WorkingDirectory=/caminho/do/projeto
Environment="PATH=/caminho/do/projeto/venv/bin"
ExecStart=/caminho/do/projeto/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Iniciar Gunicorn:**

```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# Verificar status
sudo systemctl status gunicorn.socket
```

### **12. Configurar Nginx**

```bash
sudo nano /etc/nginx/sites-available/asaas_manager
```

```nginx
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /caminho/do/projeto;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

**Ativar site:**

```bash
sudo ln -s /etc/nginx/sites-available/asaas_manager /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Restart
sudo systemctl restart nginx
```

### **13. Configurar SSL (Let's Encrypt)**

```bash
sudo certbot --nginx -d seudominio.com -d www.seudominio.com
```

Siga as instruções e escolha redirecionar HTTP para HTTPS.

### **14. Configurar Firewall**

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

### **15. Criar Diretório de Logs**

```bash
mkdir -p logs
chmod 775 logs
```

---

## Verificações Pós-Deploy

### **1. Testar o Site**

Acesse: `https://seudominio.com/login/`

- [ ] HTTPS funciona
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Pode criar clientes
- [ ] Pode criar recorrências
- [ ] Pode importar dados

### **2. Verificar Logs**

```bash
# Logs do Gunicorn
sudo journalctl -u gunicorn

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Logs da aplicação
tail -f logs/security.log
```

### **3. Verificar Status dos Serviços**

```bash
# Gunicorn
sudo systemctl status gunicorn

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

---

## Comandos Úteis

### **Restart dos Serviços**

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### **Ver Logs em Tempo Real**

```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### **Atualizar o Sistema**

```bash
cd /caminho/do/projeto
source venv/bin/activate

# Pull das mudanças
git pull

# Instalar novas dependências
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Coletar static files
python manage.py collectstatic --noinput

# Restart
sudo systemctl restart gunicorn
```

### **Backup do Banco**

```bash
# Fazer backup
sudo -u postgres pg_dump asaas_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
sudo -u postgres psql asaas_db < backup_20250103.sql
```

---

## Troubleshooting

### **Erro 502 Bad Gateway**

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status gunicorn

# Ver logs
sudo journalctl -u gunicorn -n 50
```

### **Erro 403 Forbidden**

```bash
# Verificar permissões
ls -la /caminho/do/projeto

# Ajustar permissões
chmod 755 /caminho/do/projeto
```

### **Página não carrega static files**

```bash
# Coletar novamente
python manage.py collectstatic --noinput

# Verificar configuração do Nginx
sudo nginx -t
```

### **SSL não funciona**

```bash
# Renovar certificado
sudo certbot renew

# Testar SSL
curl -I https://seudominio.com
```

---

## Manutenção

### **Atualizações de Segurança**

```bash
# Atualizar sistema
sudo apt update
sudo apt upgrade -y

# Atualizar dependências Python
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Verificar segurança
python manage.py check --deploy
```

### **Monitoramento**

Configure monitoramento de uptime:
- UptimeRobot (gratuito)
- Pingdom
- StatusCake

### **Backup Automático**

Adicione ao crontab:

```bash
crontab -e
```

```cron
# Backup diário às 2h da manhã
0 2 * * * sudo -u postgres pg_dump asaas_db > /backup/asaas_$(date +\%Y\%m\%d).sql

# Limpar backups antigos (30 dias)
0 3 * * * find /backup -name "asaas_*.sql" -mtime +30 -delete
```

---

## Checklist Final

Deploy completo:

- [ ] Sistema atualizado
- [ ] PostgreSQL instalado e configurado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] .env configurado
- [ ] Migrations executadas
- [ ] Static files coletados
- [ ] Superusuário criado
- [ ] Gunicorn configurado
- [ ] Nginx configurado
- [ ] SSL configurado
- [ ] Firewall ativado
- [ ] Logs funcionando
- [ ] Site acessível via HTTPS
- [ ] Login funciona
- [ ] Backup configurado

---

**Deploy completo! Seu sistema está no ar!** 🚀

Para mais detalhes sobre segurança, veja [SEGURANCA.md](SEGURANCA.md)

