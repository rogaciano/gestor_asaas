# 🔧 Corrigir Erros do Console - Cross-Origin-Opener-Policy

## 🚨 Problemas Identificados

1. **Cross-Origin-Opener-Policy header has been ignored** - Requer HTTPS
2. **Tracking Prevention blocked** - Recursos externos (Font Awesome CDN)
3. **Tailwind CSS via CDN** - Não recomendado para produção

## ✅ Solução Imediata (HTTP)

### 1. Ajustar Configurações de Segurança no .env

No servidor, edite o `.env`:

```bash
cd /var/www/gestor_asaas
nano .env
```

**Para HTTP (temporário até configurar HTTPS):**
```env
# Desabilitar headers que requerem HTTPS
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

# Domínio
ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br

# Subdiretório (se usar)
FORCE_SCRIPT_NAME=/gestor_asaas
```

### 2. Ajustar Settings.py (Remover Headers que Requerem HTTPS)

O Django não adiciona Cross-Origin-Opener-Policy por padrão, mas o Nginx pode estar adicionando. Verifique a configuração do Nginx.

### 3. Reiniciar Serviços

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 🔒 Solução Definitiva (HTTPS)

### 1. Configurar HTTPS com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d ga.sistema9.com.br
```

### 2. Atualizar .env para HTTPS

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

### 3. Reiniciar Serviços

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 📦 Melhorias para Produção

### 1. Usar Tailwind CSS Local (Opcional)

O aviso sobre Tailwind CDN não é crítico, mas para produção ideal seria usar Tailwind compilado localmente.

### 2. Usar Font Awesome Local (Opcional)

Para evitar problemas de Tracking Prevention, baixe Font Awesome localmente:

```bash
# No servidor
cd /var/www/gestor_asaas/static
wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2
# ... outros arquivos necessários
```

## 🔍 Verificar Configuração do Nginx

Se o Nginx estiver adicionando headers que requerem HTTPS, ajuste:

```bash
sudo nano /etc/nginx/sites-available/ga.sistema9.com.br
```

**Remova ou comente headers que requerem HTTPS (enquanto estiver em HTTP):**
```nginx
# Comentar estas linhas enquanto estiver em HTTP:
# add_header Strict-Transport-Security "max-age=31536000" always;
# add_header Cross-Origin-Opener-Policy "same-origin" always;
```

**Depois de configurar HTTPS, descomente:**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
```

## ✅ Checklist

- [ ] `.env` configurado para HTTP (temporário)
- [ ] Nginx não adiciona headers que requerem HTTPS
- [ ] Serviços reiniciados
- [ ] Testar login novamente
- [ ] Configurar HTTPS (solução definitiva)
- [ ] Atualizar `.env` para HTTPS
- [ ] Testar novamente

## 🎯 Resultado Esperado

Após configurar HTTPS:
- ✅ Sem erros de Cross-Origin-Opener-Policy
- ✅ Cookies funcionando corretamente
- ✅ Login funcionando perfeitamente
- ✅ Sem avisos de segurança no console

---

**Importante:** Os avisos sobre Tailwind CDN e Tracking Prevention são apenas avisos e não impedem o funcionamento. A prioridade é configurar HTTPS para resolver o problema do Cross-Origin-Opener-Policy.

