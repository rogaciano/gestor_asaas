#!/bin/bash
# ========================================
# Script para Resolver HTTPS - ga.sistema9.com.br
# ========================================

set -e  # Para em caso de erro

echo "=========================================="
echo "🔒 Configurando HTTPS para ga.sistema9.com.br"
echo "=========================================="
echo ""

# Cores
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

# ========================================
# Passo 1: Configurar Nginx
# ========================================

print_info "Passo 1: Configurando Nginx..."

# Criar arquivo de configuração do Nginx
sudo tee /etc/nginx/sites-available/ga.sistema9.com.br > /dev/null <<'EOF'
server {
    listen 80;
    server_name ga.sistema9.com.br;

    location /gestor_asaas {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header SCRIPT_NAME /gestor_asaas;
        proxy_redirect off;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /gestor_asaas/static/ {
        alias /var/www/gestor_asaas/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /gestor_asaas/media/ {
        alias /var/www/gestor_asaas/media/;
        expires 7d;
        access_log off;
    }
}
EOF

print_success "Arquivo de configuração do Nginx criado"

# Criar link simbólico
if [ ! -L /etc/nginx/sites-enabled/ga.sistema9.com.br ]; then
    sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/
    print_success "Link simbólico criado"
else
    print_info "Link simbólico já existe"
fi

# Testar configuração
if sudo nginx -t; then
    print_success "Configuração do Nginx válida"
    sudo systemctl restart nginx
    print_success "Nginx reiniciado"
else
    print_error "Erro na configuração do Nginx"
    exit 1
fi

# ========================================
# Passo 2: Atualizar .env
# ========================================

print_info "Passo 2: Atualizando .env..."

cd /var/www/gestor_asaas

# Backup do .env
if [ -f .env ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    print_success "Backup do .env criado"
fi

# Adicionar/atualizar configurações HTTP (antes do HTTPS)
if ! grep -q "ALLOWED_HOSTS=ga.sistema9.com.br" .env 2>/dev/null; then
    echo "" >> .env
    echo "# Domínio ga.sistema9.com.br" >> .env
    echo "ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1" >> .env
    print_success "ALLOWED_HOSTS adicionado"
fi

if ! grep -q "CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br" .env 2>/dev/null; then
    echo "CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br" >> .env
    print_success "CSRF_TRUSTED_ORIGINS adicionado"
fi

if ! grep -q "FORCE_SCRIPT_NAME=/gestor_asaas" .env 2>/dev/null; then
    echo "FORCE_SCRIPT_NAME=/gestor_asaas" >> .env
    print_success "FORCE_SCRIPT_NAME adicionado"
fi

# Garantir que está em HTTP por enquanto
sed -i 's/SESSION_COOKIE_SECURE=True/SESSION_COOKIE_SECURE=False/g' .env 2>/dev/null || true
sed -i 's/CSRF_COOKIE_SECURE=True/CSRF_COOKIE_SECURE=False/g' .env 2>/dev/null || true
sed -i 's/SECURE_SSL_REDIRECT=True/SECURE_SSL_REDIRECT=False/g' .env 2>/dev/null || true

if ! grep -q "SESSION_COOKIE_SECURE" .env 2>/dev/null; then
    echo "SESSION_COOKIE_SECURE=False" >> .env
fi
if ! grep -q "CSRF_COOKIE_SECURE" .env 2>/dev/null; then
    echo "CSRF_COOKIE_SECURE=False" >> .env
fi
if ! grep -q "SECURE_SSL_REDIRECT" .env 2>/dev/null; then
    echo "SECURE_SSL_REDIRECT=False" >> .env
fi

print_success ".env atualizado para HTTP"

# Reiniciar Gunicorn
if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    print_success "Gunicorn reiniciado"
else
    print_info "Gunicorn não está rodando (pode estar usando outro método)"
fi

# ========================================
# Passo 3: Instalar Certbot
# ========================================

print_info "Passo 3: Instalando Certbot..."

if ! command -v certbot &> /dev/null; then
    sudo apt update -qq
    sudo apt install certbot python3-certbot-nginx -y
    print_success "Certbot instalado"
else
    print_info "Certbot já está instalado"
fi

# ========================================
# Passo 4: Obter Certificado SSL
# ========================================

print_info "Passo 4: Obtendo certificado SSL..."
print_info "O Certbot vai fazer perguntas. Responda:"
print_info "  - Email: seu email"
print_info "  - Termos: A (para aceitar)"
print_info "  - Redirecionar: 2 (para redirecionar HTTP para HTTPS)"

echo ""
read -p "Pressione ENTER para continuar com o Certbot..."

sudo certbot --nginx -d ga.sistema9.com.br

print_success "Certificado SSL obtido!"

# ========================================
# Passo 5: Atualizar .env para HTTPS
# ========================================

print_info "Passo 5: Atualizando .env para HTTPS..."

# Atualizar para HTTPS
sed -i 's/SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/g' .env
sed -i 's/CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/g' .env
sed -i 's/SECURE_SSL_REDIRECT=False/SECURE_SSL_REDIRECT=True/g' .env
sed -i 's|CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br|CSRF_TRUSTED_ORIGINS=https://ga.sistema9.com.br|g' .env

# Adicionar configurações HSTS se não existirem
if ! grep -q "SECURE_HSTS_SECONDS" .env; then
    echo "SECURE_HSTS_SECONDS=31536000" >> .env
    echo "SECURE_HSTS_INCLUDE_SUBDOMAINS=True" >> .env
    echo "SECURE_HSTS_PRELOAD=True" >> .env
fi

print_success ".env atualizado para HTTPS"

# ========================================
# Passo 6: Reiniciar Serviços
# ========================================

print_info "Passo 6: Reiniciando serviços..."

sudo systemctl restart nginx
print_success "Nginx reiniciado"

if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    print_success "Gunicorn reiniciado"
fi

# ========================================
# Passo 7: Verificar Renovação
# ========================================

print_info "Passo 7: Verificando renovação automática..."

sudo certbot renew --dry-run
print_success "Renovação automática configurada"

# ========================================
# Resumo
# ========================================

echo ""
echo "=========================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "🌐 Acesse: https://ga.sistema9.com.br/gestor_asaas"
echo ""
echo "✅ O que foi feito:"
echo "   - Nginx configurado"
echo "   - Certificado SSL instalado"
echo "   - Redirecionamento HTTP → HTTPS ativado"
echo "   - .env atualizado para HTTPS"
echo "   - Serviços reiniciados"
echo ""
echo "🔒 Seu site agora está seguro com HTTPS!"
echo ""

