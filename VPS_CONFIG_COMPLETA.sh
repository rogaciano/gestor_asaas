#!/bin/bash
# Script de configuração completa para o servidor VPS
# Execute com: bash VPS_CONFIG_COMPLETA.sh

echo "=========================================="
echo "CONFIGURAÇÃO DO GESTOR ASAAS NO VPS"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variáveis (AJUSTE CONFORME SEU AMBIENTE)
PROJECT_PATH="/var/www/gestor_asaas"
VENV_PATH="$PROJECT_PATH/venv"
DOMAIN_OR_IP="144.202.29.245"
SUBDIRECTORY="/gestor_asaas"

echo -e "${YELLOW}Usando configurações:${NC}"
echo "  PROJECT_PATH: $PROJECT_PATH"
echo "  DOMAIN_OR_IP: $DOMAIN_OR_IP"
echo "  SUBDIRECTORY: $SUBDIRECTORY"
echo ""
read -p "Confirma estas configurações? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada"
    exit 1
fi

# 1. Verificar se o diretório existe
echo -e "${YELLOW}[1/10] Verificando diretório do projeto...${NC}"
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}✗ Diretório $PROJECT_PATH não existe${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Diretório encontrado${NC}"

# 2. Ativar ambiente virtual
echo -e "${YELLOW}[2/10] Ativando ambiente virtual...${NC}"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}✗ Ambiente virtual não encontrado em $VENV_PATH${NC}"
    exit 1
fi
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"

# 3. Backup do .env atual
echo -e "${YELLOW}[3/10] Fazendo backup do .env atual...${NC}"
if [ -f "$PROJECT_PATH/.env" ]; then
    cp "$PROJECT_PATH/.env" "$PROJECT_PATH/.env.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✓ Backup criado${NC}"
else
    echo -e "${YELLOW}⚠ Arquivo .env não existe, será criado${NC}"
fi

# 4. Criar/Atualizar .env
echo -e "${YELLOW}[4/10] Configurando .env...${NC}"
cat > "$PROJECT_PATH/.env" << EOF
# Django Settings
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False

# CRÍTICO: Configuração para subdiretório
FORCE_SCRIPT_NAME=$SUBDIRECTORY

# Hosts permitidos
ALLOWED_HOSTS=$DOMAIN_OR_IP,localhost,127.0.0.1

# CSRF Trusted Origins (IMPORTANTE!)
CSRF_TRUSTED_ORIGINS=http://$DOMAIN_OR_IP

# Database (SQLite para simplicidade, ou configure PostgreSQL)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=asaas_db
# DB_USER=asaas_user
# DB_PASSWORD=SUA_SENHA_AQUI
# DB_HOST=localhost
# DB_PORT=5432

# Asaas API - PRODUÇÃO
ASAAS_API_KEY=\$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjU0NGMyNWJkLTJlYjMtNDI4MS1hZWRlLWExNjJhMDIxYmRlMDo6JGFhY2hfMDQ5MjkxOTEtNTA4YS00YTViLThiM2ItY2ZlNmY2NGIwOGUz
ASAAS_API_URL=https://api.asaas.com/v3

# WhatsApp (Evolution API)
EVOLUTION_API_KEY=473315C75EDB-418B-BD1E-E9884ED04B2E
EVOLUTION_INSTANCE_ID=atitude
EVOLUTION_API_URL=https://evo.matutec.com.br
WHATSAPP_NUMBERS=5581999216560,5581996922875

# Security Settings
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
EOF

echo -e "${GREEN}✓ Arquivo .env configurado${NC}"

# 5. Verificar configuração com script Python
echo -e "${YELLOW}[5/10] Verificando configuração...${NC}"
cd "$PROJECT_PATH"
python check_config.py
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erro na verificação da configuração${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuração validada${NC}"

# 6. Coletar arquivos estáticos
echo -e "${YELLOW}[6/10] Coletando arquivos estáticos...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Arquivos estáticos coletados${NC}"

# 7. Aplicar migrations (se necessário)
echo -e "${YELLOW}[7/10] Aplicando migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations aplicadas${NC}"

# 8. Configurar permissões
echo -e "${YELLOW}[8/10] Configurando permissões...${NC}"
chown -R www-data:www-data "$PROJECT_PATH"
chmod -R 755 "$PROJECT_PATH"
chmod -R 777 "$PROJECT_PATH/logs"
echo -e "${GREEN}✓ Permissões configuradas${NC}"

# 9. Detectar servidor web e reiniciar
echo -e "${YELLOW}[9/10] Reiniciando servidor web...${NC}"

if systemctl is-active --quiet apache2; then
    echo "Detectado: Apache"
    systemctl restart apache2
    systemctl status apache2 --no-pager -l
    echo -e "${GREEN}✓ Apache reiniciado${NC}"
elif systemctl is-active --quiet nginx; then
    echo "Detectado: Nginx"
    systemctl restart nginx
    if systemctl is-active --quiet gunicorn; then
        systemctl restart gunicorn
        echo -e "${GREEN}✓ Nginx e Gunicorn reiniciados${NC}"
    else
        echo -e "${GREEN}✓ Nginx reiniciado${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Servidor web não detectado automaticamente${NC}"
    echo "Por favor, reinicie manualmente:"
    echo "  Apache: sudo systemctl restart apache2"
    echo "  Nginx: sudo systemctl restart nginx"
fi

# 10. Teste final
echo -e "${YELLOW}[10/10] Testando acesso...${NC}"
sleep 2

# Testar se a aplicação responde
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost$SUBDIRECTORY/")
if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ]; then
    echo -e "${GREEN}✓ Aplicação respondendo (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Aplicação não está respondendo corretamente (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}CONFIGURAÇÃO CONCLUÍDA!${NC}"
echo "=========================================="
echo ""
echo "URLs para testar:"
echo "  Login: http://$DOMAIN_OR_IP$SUBDIRECTORY/login/"
echo "  Home:  http://$DOMAIN_OR_IP$SUBDIRECTORY/"
echo ""
echo "IMPORTANTE: Limpe os cookies do navegador antes de testar!"
echo ""
echo "Monitorar logs:"
echo "  Django:  tail -f $PROJECT_PATH/logs/security.log"
echo "  Apache:  tail -f /var/log/apache2/error.log"
echo "  Nginx:   tail -f /var/log/nginx/error.log"
echo ""
echo "Se o login ainda não funcionar:"
echo "1. Limpe TODOS os cookies do domínio no navegador"
echo "2. Use navegação anônima para testar"
echo "3. Verifique os logs acima para mensagens de erro"
echo ""
