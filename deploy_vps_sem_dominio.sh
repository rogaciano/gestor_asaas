#!/bin/bash
# ========================================
# Script de Deploy - Asaas Manager (SEM DOMÍNIO)
# Para Ubuntu/Debian VPS - Acesso via IP
# ========================================

set -e  # Para em caso de erro

echo "=========================================="
echo "🚀 Deploy do Asaas Manager na VPS (via IP)"
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
    print_error "Por favor, execute como root (sudo bash deploy_vps_sem_dominio.sh)"
    exit 1
fi

print_info "Iniciando configuração da VPS (acesso via IP)..."
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
apt install -y git curl
print_success "Dependências instaladas"
echo ""

# ========================================
# 3. Obter IP da VPS
# ========================================
print_info "Detectando IP da VPS..."
VPS_IP=$(curl -s ifconfig.me)
print_info "IP detectado: $VPS_IP"
echo ""

# ========================================
# 4. Configurar PostgreSQL
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
# 5. Configurar Projeto
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

print_success "Projeto configurado"
echo ""

# ========================================
# 6. Configurar .env
# ========================================
print_info "Passo 5: Configurando variáveis de ambiente..."

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Solicitar API Key
read -p "API Key do Asaas (produção): " ASAAS_KEY

# Criar arquivo .env (SEM HTTPS)
cat > .env <<EOL
# Django
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$VPS_IP

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

# Security (SEM HTTPS - apenas IP)
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
EOL

print_success "Arquivo .env criado (configurado para HTTP)"
print_info "⚠️  Sistema configurado para HTTP (sem SSL)"
print_info "⚠️  Quando tiver domínio, poderá adicionar HTTPS"
echo ""

# ========================================
# 7. Migrations e Static Files
# ========================================
print_info "Passo 6: Executando migrations e coletando arquivos estáticos..."

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

print_success "Migrations e static files prontos"
echo ""

# ========================================
# 8. Criar Superusuário
# ========================================
print_info "Passo 7: Criar usuário administrador..."
echo ""
echo "⚠️  IMPORTANTE: Anote essas credenciais!"
echo ""

python manage.py createsuperuser

print_success "Superusuário criado"
echo ""

# ========================================
# 9. Configurar Gunicorn
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
# 10. Configurar Nginx (HTTP apenas)
# ========================================
print_info "Passo 9: Configurando Nginx (HTTP)..."

# Criar configuração do Nginx
cat > /etc/nginx/sites-available/asaas_manager <<EOL
server {
    listen 80;
    server_name $VPS_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
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
# 11. Configurar Firewall
# ========================================
print_info "Passo 10: Configurando firewall..."

ufw allow 'Nginx HTTP'
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
echo "   http://$VPS_IP"
echo ""
echo "⚠️  ATENÇÃO: Sistema rodando em HTTP (sem SSL)"
echo "   Quando tiver domínio, execute o script com SSL"
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
echo "1. Acesse: http://$VPS_IP/login/"
echo "2. Faça login com o usuário que você criou"
echo "3. Configure seus clientes e recorrências"
echo ""
print_info "Comandos úteis:"
echo "- Ver logs do Gunicorn: sudo journalctl -u gunicorn"
echo "- Restart Gunicorn: sudo systemctl restart gunicorn"
echo "- Restart Nginx: sudo systemctl restart nginx"
echo "- Ver status: sudo systemctl status gunicorn"
echo ""
print_info "Para adicionar HTTPS quando tiver domínio:"
echo "1. Aponte o domínio para o IP: $VPS_IP"
echo "2. Execute: sudo certbot --nginx -d seudominio.com"
echo "3. Atualize ALLOWED_HOSTS no .env"
echo "4. Atualize as configurações de segurança para True"
echo ""
print_success "Sistema pronto para uso! 🚀"
echo ""

