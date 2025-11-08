# ⏳ Aguardando Propagação DNS - ga.sistema9.com.br

Enquanto o DNS está propagando, você pode preparar tudo para quando estiver pronto.

## 🔍 Verificar Propagação DNS

### No seu computador local:

```bash
# Windows (PowerShell)
nslookup ga.sistema9.com.br

# Linux/Mac
dig ga.sistema9.com.br
# ou
nslookup ga.sistema9.com.br
```

**Resultado esperado:**
```
Name:    ga.sistema9.com.br
Address: SEU_IP_DO_SERVIDOR
```

### Verificar online:

Use ferramentas online para verificar propagação:
- https://www.whatsmydns.net/#A/ga.sistema9.com.br
- https://dnschecker.org/#A/ga.sistema9.com.br
- https://mxtoolbox.com/DNSLookup.aspx

**Quando estiver propagado:**
- ✅ Todas as localizações devem mostrar o IP do seu servidor
- ✅ Pode levar de 5 minutos a 24 horas (geralmente 1-2 horas)

## ✅ Checklist - Preparar Tudo Enquanto Aguarda

### 1. Configurar DNS no Painel

- [ ] Registro A criado: `ga` → IP do servidor
- [ ] TTL configurado (3600 ou padrão)
- [ ] Salvo e publicado

### 2. Preparar Configuração do Nginx

- [ ] Arquivo de configuração criado: `/etc/nginx/sites-available/ga.sistema9.com.br`
- [ ] Conteúdo copiado (raiz ou subdiretório)
- [ ] Link simbólico criado: `/etc/nginx/sites-enabled/ga.sistema9.com.br`
- [ ] Teste de configuração: `sudo nginx -t` (deve passar)

**IMPORTANTE:** Não reinicie o Nginx ainda se o DNS não estiver propagado!

### 3. Preparar .env no Servidor

No servidor, edite o `.env`:

```bash
cd /var/www/gestor_asaas
nano .env
```

**Configuração para HTTP (temporário):**
```env
# Domínio
ALLOWED_HOSTS=ga.sistema9.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://ga.sistema9.com.br

# Subdiretório (se usar)
FORCE_SCRIPT_NAME=/gestor_asaas

# HTTP (temporário - mudar para True depois do HTTPS)
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

# Debug (False em produção)
DEBUG=False
```

### 4. Instalar Certbot (Preparar para HTTPS)

```bash
# Atualizar sistema
sudo apt update

# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Verificar instalação
certbot --version
```

### 5. Verificar Portas do Firewall

```bash
# Verificar se portas 80 e 443 estão abertas
sudo ufw status

# Se não estiverem, abrir:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### 6. Verificar Gunicorn

```bash
# Verificar se está rodando
sudo systemctl status gunicorn

# Se não estiver, iniciar:
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 🚀 Quando DNS Estiver Propagado

### Passo 1: Testar Acesso HTTP

```bash
# No seu computador local
curl -I http://ga.sistema9.com.br

# Deve retornar HTTP 200 ou 302
```

### Passo 2: Ativar Nginx

```bash
# No servidor
sudo nginx -t
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

### Passo 3: Testar Acesso

Acesse no navegador:
- `http://ga.sistema9.com.br` (se na raiz)
- `http://ga.sistema9.com.br/gestor_asaas` (se em subdiretório)

**Deve funcionar!** (ainda sem HTTPS)

### Passo 4: Configurar HTTPS

```bash
# Obter certificado SSL
sudo certbot --nginx -d ga.sistema9.com.br

# Durante a instalação:
# - Digite seu email
# - Aceite os termos
# - Escolha redirecionar HTTP para HTTPS (Sim)
```

### Passo 5: Atualizar .env para HTTPS

```bash
cd /var/www/gestor_asaas
nano .env
```

**Atualizar para HTTPS:**
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

### Passo 6: Reiniciar Serviços

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Passo 7: Testar HTTPS

Acesse no navegador:
- `https://ga.sistema9.com.br` (se na raiz)
- `https://ga.sistema9.com.br/gestor_asaas` (se em subdiretório)

**Deve funcionar com cadeado verde!** 🔒

## 🔍 Verificar Propagação DNS - Script

Crie um script para verificar quando estiver pronto:

```bash
#!/bin/bash
# verificar_dns.sh

DOMINIO="ga.sistema9.com.br"
IP_SERVIDOR="SEU_IP_AQUI"  # Substitua pelo IP do seu servidor

echo "🔍 Verificando propagação DNS para $DOMINIO..."
echo ""

while true; do
    IP_RESOLVIDO=$(dig +short $DOMINIO | tail -1)
    
    if [ "$IP_RESOLVIDO" == "$IP_SERVIDOR" ]; then
        echo "✅ DNS PROPAGADO! IP: $IP_RESOLVIDO"
        echo "🚀 Pode configurar HTTPS agora!"
        break
    else
        echo "⏳ Aguardando... IP resolvido: $IP_RESOLVIDO (esperado: $IP_SERVIDOR)"
        sleep 60  # Verifica a cada 60 segundos
    fi
done
```

Execute:
```bash
chmod +x verificar_dns.sh
./verificar_dns.sh
```

## 📋 Resumo - O Que Fazer Agora

1. ✅ **Verificar DNS** - Use as ferramentas online
2. ✅ **Preparar Nginx** - Criar arquivo de configuração (não ativar ainda)
3. ✅ **Preparar .env** - Configurar com domínio e HTTP temporário
4. ✅ **Instalar Certbot** - Preparar para HTTPS
5. ✅ **Verificar Firewall** - Portas 80 e 443 abertas
6. ⏳ **Aguardar Propagação** - Verificar periodicamente
7. 🚀 **Quando propagar** - Ativar Nginx e configurar HTTPS

## ⚠️ Importante

- **Não reinicie o Nginx** até o DNS estar propagado
- **Não configure HTTPS** até o DNS estar propagado
- **Teste HTTP primeiro** antes de configurar HTTPS
- **Os erros do console** vão desaparecer quando configurar HTTPS

## 🎯 Próximos Passos

1. Aguardar propagação DNS (verificar a cada 30 minutos)
2. Quando propagar, seguir os passos acima
3. Configurar HTTPS
4. Atualizar .env para HTTPS
5. Testar login - deve funcionar perfeitamente!

---

**Tempo estimado de propagação:** 1-2 horas (pode levar até 24h)

