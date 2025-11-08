# 🚀 Instalar HTTPS Agora - ga.sistema9.com.br

## ✅ Passo 1: Configurar Nginx

### 1.1. Criar arquivo de configuração

```bash
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
```

### 1.2. Colar este conteúdo (SUBDIRETÓRIO `/gestor_asaas/`):

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

**OU se estiver na RAIZ, use:**

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

### 1.3. Salvar e ativar

```bash
# Salvar (Ctrl+X, Y, Enter)

# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Se OK, reiniciar
sudo systemctl restart nginx
```

## ✅ Passo 2: Atualizar .env

```bash
cd /var/www/gestor_asaas
nano .env
```

**Adicione/Atualize estas linhas:**

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

**Salvar (Ctrl+X, Y, Enter)**

**Reiniciar Gunicorn:**
```bash
sudo systemctl restart gunicorn
```

## ✅ Passo 3: Testar HTTP

Acesse no navegador:
- `http://ga.sistema9.com.br/gestor_asaas` (se subdiretório)
- `http://ga.sistema9.com.br` (se raiz)

**Deve funcionar!** Se funcionar, continue para o próximo passo.

## 🔒 Passo 4: Instalar Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

## 🔒 Passo 5: Obter Certificado SSL

```bash
sudo certbot --nginx -d ga.sistema9.com.br
```

**Durante a instalação:**
1. Digite seu email
2. Aceite os termos (A)
3. Escolha redirecionar HTTP para HTTPS (2 - Yes)

**O Certbot vai:**
- ✅ Obter o certificado SSL
- ✅ Configurar o Nginx automaticamente
- ✅ Adicionar redirecionamento HTTP → HTTPS

## ✅ Passo 6: Atualizar .env para HTTPS

```bash
cd /var/www/gestor_asaas
nano .env
```

**Altere para HTTPS:**

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

# Subdiretório (se usar)
FORCE_SCRIPT_NAME=/gestor_asaas
```

**Salvar (Ctrl+X, Y, Enter)**

## ✅ Passo 7: Reiniciar Serviços

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## ✅ Passo 8: Testar HTTPS

Acesse no navegador:
- `https://ga.sistema9.com.br/gestor_asaas` (se subdiretório)
- `https://ga.sistema9.com.br` (se raiz)

**Deve:**
- ✅ Mostrar cadeado verde 🔒
- ✅ Redirecionar HTTP → HTTPS automaticamente
- ✅ **Resolver todos os erros do console!**
- ✅ Login funcionar perfeitamente

## ✅ Passo 9: Verificar Renovação Automática

```bash
# Testar renovação
sudo certbot renew --dry-run

# Verificar timer (renovação automática)
sudo systemctl status certbot.timer
```

## 📋 Comandos Rápidos (Copie e Cole)

```bash
# 1. Configurar Nginx
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
# (cole o conteúdo acima, salve)

sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 2. Atualizar .env
cd /var/www/gestor_asaas
nano .env
# (adicione as configurações HTTP acima)

sudo systemctl restart gunicorn

# 3. Testar HTTP
# Acesse http://ga.sistema9.com.br/gestor_asaas

# 4. Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# 5. Obter certificado
sudo certbot --nginx -d ga.sistema9.com.br

# 6. Atualizar .env para HTTPS
nano .env
# (mude para HTTPS conforme acima)

# 7. Reiniciar
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 8. Testar HTTPS
# Acesse https://ga.sistema9.com.br/gestor_asaas
```

## 🎯 Resultado Final

Após seguir todos os passos:
- ✅ HTTPS configurado e funcionando
- ✅ Redirecionamento HTTP → HTTPS automático
- ✅ Sem erros de Cross-Origin-Opener-Policy
- ✅ Cookies seguros funcionando
- ✅ Login funcionando perfeitamente
- ✅ Certificado renovado automaticamente

## 🆘 Se Algo Der Errado

### Erro: "Nginx test failed"

```bash
# Verificar erros
sudo nginx -t

# Ver logs
sudo tail -50 /var/log/nginx/error.log
```

### Erro: "Certbot não consegue validar"

```bash
# Verificar se porta 80 está aberta
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar se Nginx está rodando
sudo systemctl status nginx

# Ver logs do Certbot
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

### Erro: "502 Bad Gateway"

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status gunicorn

# Ver logs
sudo journalctl -u gunicorn -n 50
```

---

**Pronto! Siga os passos acima e seu HTTPS estará funcionando!** 🚀

