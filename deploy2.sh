
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

