# 🌐 Configurar Domínio e HTTPS - ga.sistema9.com.br

Este guia mostra como configurar o domínio `ga.sistema9.com.br` e habilitar HTTPS com Let's Encrypt.

## 📋 Pré-requisitos

- Servidor VPS com acesso root
- Domínio `ga.sistema9.com.br` apontando para o IP do servidor
- Nginx ou Apache instalado
- Portas 80 e 443 abertas no firewall

## 🔧 Passo 1: Configurar DNS

### No painel do seu provedor de domínio:

1. Acesse o painel de DNS
2. Adicione um registro **A**:
   - **Nome/Host:** `ga` (ou `ga.sistema9.com.br` dependendo do painel)
   - **Tipo:** A
   - **Valor/IP:** IP do seu servidor VPS
   - **TTL:** 3600 (ou padrão)

### Verificar DNS:

```bash
# No seu computador local
nslookup ga.sistema9.com.br
# ou
dig ga.sistema9.com.br

# Deve retornar o IP do seu servidor
```

**Aguarde a propagação DNS (pode levar até 24h, geralmente 1-2h)**

## 🔧 Passo 2: Configurar Nginx

### 2.1. Criar arquivo de configuração do Nginx

```bash
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
```

**Conteúdo (se estiver na raiz):**
```nginx
server {
    listen 80;
    server_name ga.sistema9.com.br;

    # Redireciona para HTTPS (depois de configurar SSL)
    # return 301 https://$server_name$request_uri;

    # Por enquanto, aceita HTTP
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Arquivos estáticos
    location /static/ {
        alias /var/www/gestor_asaas/staticfiles/;
    }

    # Arquivos de mídia (se houver)
    location /media/ {
        alias /var/www/gestor_asaas/media/;
    }
}
```

**Conteúdo (se estiver em subdiretório `/gestor_asaas/`):**
```nginx
server {
    listen 80;
    server_name ga.sistema9.com.br;

    # Redireciona para HTTPS (depois de configurar SSL)
    # return 301 https://$server_name$request_uri;

    # Por enquanto, aceita HTTP
    location /gestor_asaas {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header SCRIPT_NAME /gestor_asaas;
        proxy_redirect off;
    }

    # Arquivos estáticos
    location /gestor_asaas/static/ {
        alias /var/www/gestor_asaas/staticfiles/;
    }
}
```

### 2.2. Ativar o site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Se estiver OK, reiniciar Nginx
sudo systemctl restart nginx
```

### 2.3. Verificar se está funcionando

```bash
# Verificar status
sudo systemctl status nginx

# Verificar logs
sudo tail -f /var/log/nginx/error.log
```

## 🔧 Passo 3: Atualizar Configurações do Django

### 3.1. Editar .env no servidor

```bash
cd /var/www/gestor_asaas
nano .env
```

**Atualize as seguintes variáveis:**

```env
# Domínio
ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://ga.sistema9.com.br,http://ga.sistema9.com.br

# Se estiver em subdiretório
FORCE_SCRIPT_NAME=/gestor_asaas

# Se NÃO estiver em subdiretório, deixe vazio
# FORCE_SCRIPT_NAME=

# HTTPS (será True depois de configurar SSL)
SESSION_COOKIE_SECURE=False  # Mude para True depois do HTTPS
CSRF_COOKIE_SECURE=False     # Mude para True depois do HTTPS
SECURE_SSL_REDIRECT=False    # Mude para True depois do HTTPS
```

### 3.2. Reiniciar Gunicorn

```bash
sudo systemctl restart gunicorn
# ou
sudo systemctl restart apache2
```

### 3.3. Testar acesso

Acesse no navegador:
- `http://ga.sistema9.com.br` (se na raiz)
- `http://ga.sistema9.com.br/gestor_asaas` (se em subdiretório)

## 🔒 Passo 4: Configurar HTTPS com Let's Encrypt

### 4.1. Instalar Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### 4.2. Obter certificado SSL

```bash
# Se estiver na raiz
sudo certbot --nginx -d ga.sistema9.com.br

# Se estiver em subdiretório, use:
sudo certbot --nginx -d ga.sistema9.com.br --webroot-path=/var/www/gestor_asaas/staticfiles
```

**Durante a instalação:**
- Digite seu email
- Aceite os termos
- Escolha se quer redirecionar HTTP para HTTPS (recomendado: Sim)

### 4.3. Verificar renovação automática

```bash
# Testar renovação
sudo certbot renew --dry-run

# Verificar timer do systemd
sudo systemctl status certbot.timer
```

### 4.4. Atualizar configuração do Nginx (Certbot faz automaticamente)

O Certbot atualiza automaticamente o arquivo do Nginx. Verifique:

```bash
sudo cat /etc/nginx/sites-available/ga.sistema9.com.br
```

Deve ter algo como:
```nginx
server {
    listen 443 ssl;
    server_name ga.sistema9.com.br;

    ssl_certificate /etc/letsencrypt/live/ga.sistema9.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ga.sistema9.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... resto da configuração
}

server {
    listen 80;
    server_name ga.sistema9.com.br;
    return 301 https://$server_name$request_uri;
}
```

### 4.5. Atualizar .env para HTTPS

```bash
cd /var/www/gestor_asaas
nano .env
```

**Altere para:**
```env
# HTTPS ativado
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Domínio
ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://ga.sistema9.com.br
```

### 4.6. Reiniciar serviços

```bash
# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar Gunicorn
sudo systemctl restart gunicorn
```

## ✅ Passo 5: Verificar Tudo

### 5.1. Testar acesso HTTPS

Acesse no navegador:
- `https://ga.sistema9.com.br` (se na raiz)
- `https://ga.sistema9.com.br/gestor_asaas` (se em subdiretório)

Deve mostrar:
- ✅ Cadeado verde (HTTPS seguro)
- ✅ Página carrega normalmente
- ✅ Login funciona

### 5.2. Verificar redirecionamento HTTP → HTTPS

Acesse:
- `http://ga.sistema9.com.br`

Deve redirecionar automaticamente para `https://ga.sistema9.com.br`

### 5.3. Verificar certificado SSL

```bash
# Verificar certificado
openssl s_client -connect ga.sistema9.com.br:443 -servername ga.sistema9.com.br

# Ou use ferramenta online:
# https://www.ssllabs.com/ssltest/analyze.html?d=ga.sistema9.com.br
```

## 🔧 Configuração Completa do Nginx (Exemplo)

### Se estiver na raiz:

```nginx
server {
    listen 443 ssl http2;
    server_name ga.sistema9.com.br;

    ssl_certificate /etc/letsencrypt/live/ga.sistema9.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ga.sistema9.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Segurança adicional
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy para Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Arquivos estáticos
    location /static/ {
        alias /var/www/gestor_asaas/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Arquivos de mídia
    location /media/ {
        alias /var/www/gestor_asaas/media/;
    }
}

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name ga.sistema9.com.br;
    return 301 https://$server_name$request_uri;
}
```

### Se estiver em subdiretório `/gestor_asaas/`:

```nginx
server {
    listen 443 ssl http2;
    server_name ga.sistema9.com.br;

    ssl_certificate /etc/letsencrypt/live/ga.sistema9.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ga.sistema9.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Segurança adicional
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy para Gunicorn com subdiretório
    location /gestor_asaas {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header SCRIPT_NAME /gestor_asaas;
        proxy_redirect off;
    }

    # Arquivos estáticos
    location /gestor_asaas/static/ {
        alias /var/www/gestor_asaas/staticfiles/;
        expires 30d;
    }
}

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name ga.sistema9.com.br;
    return 301 https://$server_name$request_uri;
}
```

## 📋 Checklist Final

- [ ] DNS configurado e propagado (verificar com `nslookup`)
- [ ] Nginx configurado e funcionando
- [ ] Acesso HTTP funcionando (`http://ga.sistema9.com.br`)
- [ ] `.env` atualizado com `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`
- [ ] Certbot instalado
- [ ] Certificado SSL obtido
- [ ] Nginx atualizado com SSL
- [ ] `.env` atualizado para HTTPS (`SESSION_COOKIE_SECURE=True`, etc.)
- [ ] Acesso HTTPS funcionando (`https://ga.sistema9.com.br`)
- [ ] Redirecionamento HTTP → HTTPS funcionando
- [ ] Login funcionando com HTTPS
- [ ] Renovação automática do certificado configurada

## 🔍 Troubleshooting

### Problema: DNS não resolve

```bash
# Verificar se o DNS está propagado
nslookup ga.sistema9.com.br
dig ga.sistema9.com.br

# Se não resolver, aguarde mais tempo (pode levar até 24h)
```

### Problema: Certbot não consegue validar

```bash
# Verificar se a porta 80 está aberta
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar se o Nginx está rodando
sudo systemctl status nginx

# Verificar logs do Certbot
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Problema: Erro 502 Bad Gateway

```bash
# Verificar se o Gunicorn está rodando
sudo systemctl status gunicorn

# Verificar logs do Gunicorn
sudo journalctl -u gunicorn -n 50

# Verificar se a porta 8000 está correta
sudo netstat -tlnp | grep 8000
```

### Problema: Cookies não funcionam com HTTPS

```bash
# Verificar .env
cat .env | grep SESSION_COOKIE_SECURE
# Deve ser: SESSION_COOKIE_SECURE=True

# Reiniciar Gunicorn
sudo systemctl restart gunicorn
```

## 📝 Resumo das Mudanças

| Item | Antes | Depois |
|------|-------|--------|
| URL | `http://IP` | `https://ga.sistema9.com.br` |
| ALLOWED_HOSTS | IP | `ga.sistema9.com.br` |
| CSRF_TRUSTED_ORIGINS | IP | `https://ga.sistema9.com.br` |
| SESSION_COOKIE_SECURE | False | True |
| CSRF_COOKIE_SECURE | False | True |
| SECURE_SSL_REDIRECT | False | True |

---

**Pronto!** Agora você tem:
- ✅ Domínio configurado
- ✅ HTTPS ativado
- ✅ Redirecionamento HTTP → HTTPS
- ✅ Certificado SSL renovado automaticamente

