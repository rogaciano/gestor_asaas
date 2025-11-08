# 🔧 Corrigir Nginx Antes do Certbot

## ❌ Erro Encontrado

```
open() "/etc/nginx/sites-enabled/ga.sistema9.com.br" failed (2: No such file or directory)
```

O arquivo de configuração do Nginx não existe. Vamos criar agora!

## ✅ Solução: Execute Estes Comandos

### Passo 1: Criar Arquivo de Configuração do Nginx

```bash
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
```

**Cole este conteúdo completo:**

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

**Salvar:** Pressione `Ctrl+X`, depois `Y`, depois `Enter`

### Passo 2: Criar Link Simbólico

```bash
sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/
```

### Passo 3: Testar Configuração do Nginx

```bash
sudo nginx -t
```

**Deve mostrar:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Passo 4: Reiniciar Nginx

```bash
sudo systemctl restart nginx
```

### Passo 5: Verificar Status

```bash
sudo systemctl status nginx
```

**Deve mostrar:** `active (running)`

### Passo 6: Agora Executar Certbot

```bash
sudo certbot --nginx -d ga.sistema9.com.br
```

**Durante a instalação:**
- Digite seu email
- Aceite os termos (digite `A` e Enter)
- Escolha redirecionar HTTP para HTTPS (digite `2` e Enter)

## ✅ Comandos Completos (Copie e Cole)

```bash
# 1. Criar arquivo de configuração
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

# 2. Criar link simbólico
sudo ln -s /etc/nginx/sites-available/ga.sistema9.com.br /etc/nginx/sites-enabled/

# 3. Testar configuração
sudo nginx -t

# 4. Reiniciar Nginx
sudo systemctl restart nginx

# 5. Verificar status
sudo systemctl status nginx

# 6. Executar Certbot
sudo certbot --nginx -d ga.sistema9.com.br
```

## 🆘 Se Ainda Der Erro

### Verificar se o arquivo foi criado:

```bash
ls -la /etc/nginx/sites-available/ga.sistema9.com.br
ls -la /etc/nginx/sites-enabled/ga.sistema9.com.br
```

### Ver logs do Nginx:

```bash
sudo tail -50 /var/log/nginx/error.log
```

### Verificar se a porta 80 está aberta:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

**Execute os comandos acima e depois rode o Certbot novamente!** 🚀

