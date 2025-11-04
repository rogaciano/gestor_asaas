#!/bin/bash
# ========================================
# Script de Deploy - Asaas Manager
# Para VPS com SUBDIRETÓRIO (http://IP/asaas/)
# ========================================

set -e  # Para em caso de erro

echo "=========================================="
echo "🚀 Deploy com Subdiretório"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
    print_error "Execute como root: sudo bash deploy_vps_com_subdiretorio.sh"
    exit 1
fi

print_info "Iniciando configuração..."
echo ""

# ========================================
# 1. Obter IP e Subdiretório
# ========================================
print_info "Detectando IP da VPS..."
VPS_IP=$(curl -s ifconfig.me)
print_info "IP detectado: $VPS_IP"
echo ""

read -p "Nome do subdiretório [asaas]: " SUBDIR
SUBDIR=${SUBDIR:-asaas}
print_info "Subdiretório: /$SUBDIR"
print_info "URL de acesso será: http://$VPS_IP/$SUBDIR/"
echo ""

# ========================================
# 2. Atualizar Sistema
# ========================================
print_info "Atualizando sistema..."
apt update
apt upgrade -y
print_success "Sistema atualizado"
echo ""

# ========================================
# 3. Instalar Dependências
# ========================================
print_info "Instalando dependências..."
apt install -y python3 python3-pip python3-venv python3-dev
apt install -y postgresql postgresql-contrib libpq-dev
apt install -y nginx git curl
print_success "Dependências instaladas"
echo ""

# ========================================
# 4. Configurar PostgreSQL
# ========================================
print_info "Configurando PostgreSQL..."

read -p "Nome do banco [asaas_db]: " DB_NAME
DB_NAME=${DB_NAME:-asaas_db}

read -p "Usuário do banco [asaas_user]: " DB_USER
DB_USER=${DB_USER:-asaas_user}

read -sp "Senha do banco (deixe em branco para gerar): " DB_PASSWORD
echo ""
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32)
    print_info "Senha gerada: $DB_PASSWORD"
fi

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
# 5. Configurar Projeto
# ========================================
print_info "Configurando projeto..."

PROJECT_DIR=$(pwd)
print_info "Diretório: $PROJECT_DIR"

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

print_success "Projeto configurado"
echo ""

# ========================================
# 6. Configurar .env
# ========================================
print_info "Configurando .env..."

SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

read -p "API Key do Asaas (produção): " ASAAS_KEY

cat > .env <<EOL
# Django
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$VPS_IP

# Subdiretório
FORCE_SCRIPT_NAME=/$SUBDIR

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

# Security (HTTP)
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
EOL

print_success ".env criado"
echo ""

# ========================================
# 7. Migrations e Static Files
# ========================================
print_info "Executando migrations..."

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

print_success "Migrations concluídas"
echo ""

# ========================================
# 8. Criar Superusuário
# ========================================
print_info "Criar usuário administrador..."
echo ""
python manage.py createsuperuser
print_success "Superusuário criado"
echo ""

# ========================================
# 9. Configurar Gunicorn
# ========================================
print_info "Configurando Gunicorn..."

cat > /etc/systemd/system/gunicorn-$SUBDIR.socket <<EOL
[Unit]
Description=gunicorn socket ($SUBDIR)

[Socket]
ListenStream=/run/gunicorn-$SUBDIR.sock

[Install]
WantedBy=sockets.target
EOL

cat > /etc/systemd/system/gunicorn-$SUBDIR.service <<EOL
[Unit]
Description=gunicorn daemon ($SUBDIR)
Requires=gunicorn-$SUBDIR.socket
After=network.target

[Service]
User=$SUDO_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn-$SUBDIR.sock \\
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

systemctl start gunicorn-$SUBDIR.socket
systemctl enable gunicorn-$SUBDIR.socket

print_success "Gunicorn configurado"
echo ""

# ========================================
# 10. Configurar Nginx
# ========================================
print_info "Configurando Nginx..."

# Criar configuração
cat > /etc/nginx/sites-available/asaas_$SUBDIR <<EOL
# Configuração para http://$VPS_IP/$SUBDIR/

location /$SUBDIR {
    rewrite ^/$SUBDIR(.*)\$ \$1 break;
    include proxy_params;
    proxy_pass http://unix:/run/gunicorn-$SUBDIR.sock;
    proxy_set_header X-Forwarded-Prefix /$SUBDIR;
    proxy_set_header X-Script-Name /$SUBDIR;
}

location /$SUBDIR/static/ {
    alias $PROJECT_DIR/staticfiles/;
}
EOL

# Adicionar ao default ou criar include
if grep -q "include /etc/nginx/sites-available/asaas_" /etc/nginx/sites-available/default; then
    print_info "Nginx já tem includes configurados"
else
    # Adicionar include no server block do default
    sed -i '/server_name _;/a\    include /etc/nginx/sites-available/asaas_*;' /etc/nginx/sites-available/default
fi

# Testar configuração
nginx -t

# Restart Nginx
systemctl restart nginx

print_success "Nginx configurado"
echo ""

# ========================================
# 11. Configurar Firewall
# ========================================
print_info "Configurando firewall..."

ufw allow 'Nginx HTTP'
ufw allow OpenSSH
ufw --force enable

print_success "Firewall configurado"
echo ""

# ========================================
# 12. Criar logs
# ========================================
mkdir -p $PROJECT_DIR/logs
chown -R $SUDO_USER:www-data $PROJECT_DIR/logs
chmod -R 775 $PROJECT_DIR/logs

print_success "Logs configurados"
echo ""

# ========================================
# FINALIZAÇÃO
# ========================================
echo ""
echo "=========================================="
print_success "🎉 DEPLOY CONCLUÍDO!"
echo "=========================================="
echo ""
echo "📊 INFORMAÇÕES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URL de Acesso:"
echo "   http://$VPS_IP/$SUBDIR/"
echo ""
echo "🔐 Login:"
echo "   http://$VPS_IP/$SUBDIR/login/"
echo ""
echo "🗄️ Banco de Dados:"
echo "   Nome: $DB_NAME"
echo "   Usuário: $DB_USER"
echo "   Senha: $DB_PASSWORD"
echo ""
echo "⚠️ IMPORTANTE: Anote essas informações!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "Comandos úteis:"
echo "- Logs: sudo journalctl -u gunicorn-$SUBDIR -f"
echo "- Restart: sudo systemctl restart gunicorn-$SUBDIR"
echo "- Status: sudo systemctl status gunicorn-$SUBDIR"
echo ""
print_success "Sistema pronto! Acesse: http://$VPS_IP/$SUBDIR/"
echo ""

