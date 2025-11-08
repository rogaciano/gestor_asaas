# 🔧 Comandos para Resolver HTTPS - ga.sistema9.com.br

## 🚀 Execute Estes Comandos no Servidor

### Opção 1: Usar o Script Automático (Recomendado)

```bash
# 1. Baixar o script
cd /var/www/gestor_asaas
wget https://raw.githubusercontent.com/rogaciano/gestor_asaas/main/resolver_https_comandos.sh

# 2. Tornar executável
chmod +x resolver_https_comandos.sh

# 3. Executar
sudo ./resolver_https_comandos.sh
```

### Opção 2: Comandos Manuais (Passo a Passo)

#### Passo 1: Configurar Nginx

```bash
# Criar arquivo de configuração
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
```

**Cole este conteúdo:**
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

**Salvar (Ctrl+X, Y, Enter) e continuar:**

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

#### Passo 2: Atualizar .env

```bash
cd /var/www/gestor_asaas

# Fazer backup
cp .env .env.backup

# Editar .env
nano .env
```

**Adicione/Atualize estas linhas:**
```env
ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br
FORCE_SCRIPT_NAME=/gestor_asaas
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
```

**Salvar (Ctrl+X, Y, Enter) e continuar:**

```bash
# Reiniciar Gunicorn
sudo systemctl restart gunicorn
```

#### Passo 3: Instalar Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

#### Passo 4: Obter Certificado SSL

```bash
sudo certbot --nginx -d ga.sistema9.com.br
```

**Durante a instalação:**
- Digite seu email
- Aceite os termos (digite `A` e Enter)
- Escolha redirecionar HTTP para HTTPS (digite `2` e Enter)

#### Passo 5: Atualizar .env para HTTPS

```bash
cd /var/www/gestor_asaas
nano .env
```

**Altere para:**
```env
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
CSRF_TRUSTED_ORIGINS=https://ga.sistema9.com.br
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

**Salvar (Ctrl+X, Y, Enter) e continuar:**

#### Passo 6: Reiniciar Serviços

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

#### Passo 7: Verificar Renovação

```bash
sudo certbot renew --dry-run
```

## ✅ Testar

Acesse no navegador:
- `https://ga.sistema9.com.br/gestor_asaas`

**Deve:**
- ✅ Mostrar cadeado verde 🔒
- ✅ Sem erros de certificado
- ✅ Login funcionando

## 🆘 Se Der Erro

### Erro: "Nginx test failed"

```bash
# Ver erros
sudo nginx -t

# Ver logs
sudo tail -50 /var/log/nginx/error.log
```

### Erro: "Certbot não consegue validar"

```bash
# Verificar portas
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar Nginx
sudo systemctl status nginx

# Ver logs do Certbot
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

### Erro: "502 Bad Gateway"

```bash
# Verificar Gunicorn
sudo systemctl status gunicorn

# Ver logs
sudo journalctl -u gunicorn -n 50
```

---

**Pronto! Siga os comandos acima e o HTTPS estará funcionando!** 🚀

