#!/bin/bash
# ========================================
# Script de Deploy - Asaas Manager
# Para Ubuntu/Debian VPS
# ========================================

set -e  # Para em caso de erro

echo "=========================================="
echo "🚀 Deploy do Asaas Manager na VPS"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para print colorido
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    print_error "Por favor, execute como root (sudo bash deploy_vps.sh)"
    exit 1
fi

print_info "Iniciando configuração da VPS..."
echo ""

# ========================================
# 1. Atualizar Sistema
# ========================================
print_info "Passo 1: Atualizando sistema..."
apt update
apt upgrade -y
print_success "Sistema atualizado"
echo ""

# ========================================
# 2. Instalar Dependências
# ========================================
print_info "Passo 2: Instalando dependências..."
apt install -y python3 python3-pip python3-venv python3-dev
apt install -y postgresql postgresql-contrib libpq-dev
apt install -y nginx
apt install -y certbot python3-certbot-nginx
apt install -y git curl
print_success "Dependências instaladas"
echo ""

# ========================================
# 3. Configurar PostgreSQL
# ========================================
print_info "Passo 3: Configurando PostgreSQL..."

# Solicitar informações do banco
read -p "Nome do banco de dados [asaas_db]: " DB_NAME
DB_NAME=${DB_NAME:-asaas_db}

read -p "Usuário do banco [asaas_user]: " DB_USER
DB_USER=${DB_USER:-asaas_user}

read -sp "Senha do banco (será gerada automaticamente se deixar em branco): " DB_PASSWORD
echo ""
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32)
    print_info "Senha gerada automaticamente: $DB_PASSWORD"
fi

# Criar banco e usuário
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

print_success "PostgreSQL configurado"
echo ""

# ========================================
# 4. Configurar Projeto
# ========================================
print_info "Passo 4: Configurando projeto..."

# Obter diretório do projeto
PROJECT_DIR=$(pwd)
print_info "Diretório do projeto: $PROJECT_DIR"

# Criar ambiente virtual
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

print_success "Projeto configurado"
echo ""

# ========================================
# 5. Configurar .env
# ========================================
print_info "Passo 5: Configurando variáveis de ambiente..."

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Solicitar informações
read -p "Domínio da VPS (ex: seusite.com): " DOMAIN
read -p "API Key do Asaas (produção): " ASAAS_KEY

# Criar arquivo .env
cat > .env <<EOL
# Django
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Asaas API
ASAAS_API_KEY=$ASAAS_KEY
ASAAS_API_URL=https://api.asaas.com/v3

# Security (HTTPS)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
EOL

print_success "Arquivo .env criado"
echo ""

# ========================================
# 6. Migrations e Static Files
# ========================================
print_info "Passo 6: Executando migrations e coletando arquivos estáticos..."

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

print_success "Migrations e static files prontos"
echo ""

# ========================================
# 7. Criar Superusuário
# ========================================
print_info "Passo 7: Criar usuário administrador..."
echo ""
echo "⚠️  IMPORTANTE: Anote essas credenciais!"
echo ""

python manage.py createsuperuser

print_success "Superusuário criado"
echo ""

# ========================================
# 8. Configurar Gunicorn
# ========================================
print_info "Passo 8: Configurando Gunicorn..."

# Criar arquivo de socket
cat > /etc/systemd/system/gunicorn.socket <<EOL
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOL

# Criar arquivo de serviço
cat > /etc/systemd/system/gunicorn.service <<EOL
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$SUDO_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn.sock \\
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

# Iniciar e habilitar Gunicorn
systemctl start gunicorn.socket
systemctl enable gunicorn.socket

print_success "Gunicorn configurado"
echo ""

# ========================================
# 9. Configurar Nginx
# ========================================
print_info "Passo 9: Configurando Nginx..."

# Criar configuração do Nginx
cat > /etc/nginx/sites-available/asaas_manager <<EOL
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOL

# Ativar site
ln -sf /etc/nginx/sites-available/asaas_manager /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Restart Nginx
systemctl restart nginx

print_success "Nginx configurado"
echo ""

# ========================================
# 10. Configurar SSL (Let's Encrypt)
# ========================================
print_info "Passo 10: Configurando SSL (HTTPS)..."

certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

print_success "SSL configurado"
echo ""

# ========================================
# 11. Configurar Firewall
# ========================================
print_info "Passo 11: Configurando firewall..."

ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

print_success "Firewall configurado"
echo ""

# ========================================
# 12. Criar diretório de logs
# ========================================
mkdir -p $PROJECT_DIR/logs
chown -R $SUDO_USER:www-data $PROJECT_DIR/logs
chmod -R 775 $PROJECT_DIR/logs

print_success "Diretórios criados"
echo ""

# ========================================
# FINALIZAÇÃO
# ========================================
echo ""
echo "=========================================="
print_success "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=========================================="
echo ""
echo "📊 INFORMAÇÕES DO DEPLOY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URL do Sistema:"
echo "   https://$DOMAIN"
echo ""
echo "🔐 Banco de Dados:"
echo "   Nome: $DB_NAME"
echo "   Usuário: $DB_USER"
echo "   Senha: $DB_PASSWORD"
echo ""
echo "⚠️  IMPORTANTE: Guarde essas informações em local seguro!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "Próximos passos:"
echo "1. Acesse: https://$DOMAIN/login/"
echo "2. Faça login com o usuário que você criou"
echo "3. Configure seus clientes e recorrências"
echo ""
print_info "Comandos úteis:"
echo "- Ver logs do Gunicorn: journalctl -u gunicorn"
echo "- Restart Gunicorn: systemctl restart gunicorn"
echo "- Restart Nginx: systemctl restart nginx"
echo "- Ver status: systemctl status gunicorn"
echo ""
print_success "Sistema pronto para uso! 🚀"
echo ""

