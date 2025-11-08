# ✅ Checklist: Quando DNS Estiver Propagado

## 🔍 Passo 1: Verificar Propagação DNS

```bash
# No seu computador local
nslookup ga.sistema9.com.br
# ou
dig ga.sistema9.com.br

# Deve retornar o IP do seu servidor VPS
```

**Aguarde até o DNS propagar (pode levar 1-24h, geralmente 1-2h)**

## 🚀 Passo 2: Configurar Nginx

### 2.1. Criar arquivo de configuração

```bash
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
```

### 2.2. Colar conteúdo (escolha uma opção):

**Se estiver em SUBDIRETÓRIO `/gestor_asaas/` (use este):**
```nginx
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
```

**Se estiver na RAIZ:**
```nginx
server {
    listen 80;
    server_name ga.sistema9.com.br;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /var/www/gestor_asaas/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias /var/www/gestor_asaas/media/;
        expires 7d;
        access_log off;
    }
}
```

### 2.3. Ativar e testar

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Se OK, reiniciar
sudo systemctl restart nginx
```

## 🔧 Passo 3: Atualizar .env no Servidor

```bash
cd /var/www/gestor_asaas
nano .env
```

**Adicione/Atualize:**
```env
# Domínio
ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br

# HTTP (antes do HTTPS)
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False

# Subdiretório (se usar)
FORCE_SCRIPT_NAME=/gestor_asaas
```

**Reinicie Gunicorn:**
```bash
sudo systemctl restart gunicorn
```

## ✅ Passo 4: Testar Acesso HTTP

Acesse no navegador:
- `http://ga.sistema9.com.br/gestor_asaas` (se subdiretório)
- `http://ga.sistema9.com.br` (se raiz)

**Deve funcionar!** (ainda sem HTTPS, mas funcionando)

## 🔒 Passo 5: Configurar HTTPS

### 5.1. Instalar Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### 5.2. Obter Certificado SSL

```bash
sudo certbot --nginx -d ga.sistema9.com.br
```

**Durante a instalação:**
- Digite seu email
- Aceite os termos
- Escolha redirecionar HTTP para HTTPS (Sim)

### 5.3. Atualizar .env para HTTPS

```bash
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

### 5.4. Reiniciar Serviços

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## ✅ Passo 6: Testar HTTPS

Acesse:
- `https://ga.sistema9.com.br/gestor_asaas` (se subdiretório)
- `https://ga.sistema9.com.br` (se raiz)

**Deve:**
- ✅ Mostrar cadeado verde
- ✅ Redirecionar HTTP → HTTPS automaticamente
- ✅ **Resolver todos os erros do console!**
- ✅ Login funcionar perfeitamente

## 📋 Resumo dos Comandos

```bash
# 1. Verificar DNS
nslookup ga.sistema9.com.br

# 2. Configurar Nginx
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
# (cole o conteúdo acima)

sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 3. Atualizar .env
cd /var/www/gestor_asaas
nano .env
# (adicione as configurações acima)

sudo systemctl restart gunicorn

# 4. Testar HTTP
# Acesse http://ga.sistema9.com.br/gestor_asaas

# 5. Configurar HTTPS
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ga.sistema9.com.br

# 6. Atualizar .env para HTTPS
nano .env
# (mude para HTTPS conforme acima)

sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 7. Testar HTTPS
# Acesse https://ga.sistema9.com.br/gestor_asaas
```

## 🎯 Resultado Final

Após configurar HTTPS:
- ✅ Sem erros de Cross-Origin-Opener-Policy
- ✅ Sem avisos de Tracking Prevention
- ✅ Cookies seguros funcionando
- ✅ Login funcionando perfeitamente
- ✅ Sistema totalmente seguro

---

**Aguarde a propagação DNS e siga este checklist!** 🚀

