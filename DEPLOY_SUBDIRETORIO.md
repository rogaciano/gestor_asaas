# 🚀 Deploy com Subdiretório (http://IP/asaas/)

## ✅ Para Servidores com Múltiplos Projetos

Quando você tem vários projetos no mesmo IP, cada um precisa estar em um subdiretório diferente.

**Exemplo:**
```
http://123.456.789.012/asaas/      <- Seu projeto
http://123.456.789.012/outro/      <- Outro projeto
http://123.456.789.012/site/       <- Outro site
```

---

## ⚡ Deploy Rápido

### **Comando único:**

```bash
sudo bash deploy_vps_com_subdiretorio.sh
```

**Durante a execução, será perguntado:**
- Nome do subdiretório (padrão: `asaas`)

---

## 🌐 URL de Acesso

Após o deploy:

```
http://SEU_IP/asaas/
http://SEU_IP/asaas/login/
```

**Exemplo:**
```
http://123.456.789.012/asaas/
http://123.456.789.012/asaas/login/
```

---

## 📋 O Que o Script Faz

### **1. Detecta o IP automaticamente**
```
IP detectado: 123.456.789.012
```

### **2. Pergunta o subdiretório**
```
Nome do subdiretório [asaas]: _
```

Pode usar qualquer nome:
- `asaas`
- `sistema`
- `app`
- `manager`
- etc.

### **3. Configura tudo automaticamente:**

**Django settings.py:**
```python
FORCE_SCRIPT_NAME = '/asaas'
STATIC_URL = '/asaas/static/'
```

**Nginx:**
```nginx
location /asaas {
    proxy_pass http://unix:/run/gunicorn-asaas.sock;
}

location /asaas/static/ {
    alias /caminho/staticfiles/;
}
```

**Gunicorn:**
- Socket único: `/run/gunicorn-asaas.sock`
- Service único: `gunicorn-asaas.service`

---

## 🔧 Configuração Técnica

### **FORCE_SCRIPT_NAME**

O Django usa `FORCE_SCRIPT_NAME` para funcionar em subdiretórios:

```python
# config/settings.py (já configurado automaticamente)
FORCE_SCRIPT_NAME = '/asaas'
```

Isso faz com que todas as URLs sejam geradas com o prefixo `/asaas/`:
- `/` vira `/asaas/`
- `/login/` vira `/asaas/login/`
- `/clientes/` vira `/asaas/clientes/`

### **Nginx com Subdiretório**

O Nginx faz o roteamento:

```nginx
location /asaas {
    rewrite ^/asaas(.*)$ $1 break;
    proxy_pass http://unix:/run/gunicorn-asaas.sock;
    proxy_set_header X-Forwarded-Prefix /asaas;
}
```

- Remove `/asaas` antes de passar para o Django
- Adiciona header para o Django saber o prefixo

---

## 📝 Passo a Passo Manual

Se preferir configurar manualmente:

### **1. Editar settings.py**

```python
# config/settings.py
FORCE_SCRIPT_NAME = '/asaas'
STATIC_URL = '/asaas/static/'
```

### **2. Atualizar .env**

```env
FORCE_SCRIPT_NAME=/asaas
```

### **3. Configurar Nginx**

```bash
sudo nano /etc/nginx/sites-available/default
```

Adicionar dentro do `server` block:

```nginx
location /asaas {
    rewrite ^/asaas(.*)$ $1 break;
    include proxy_params;
    proxy_pass http://unix:/run/gunicorn-asaas.sock;
    proxy_set_header X-Forwarded-Prefix /asaas;
    proxy_set_header X-Script-Name /asaas;
}

location /asaas/static/ {
    alias /caminho/do/projeto/staticfiles/;
}
```

### **4. Coletar static files novamente**

```bash
python manage.py collectstatic --noinput
```

### **5. Restart**

```bash
sudo systemctl restart gunicorn-asaas
sudo systemctl restart nginx
```

---

## ✅ Testando

### **1. Acessar a raiz do subdiretório:**
```
http://SEU_IP/asaas/
```

Deve redirecionar para login.

### **2. Acessar o login:**
```
http://SEU_IP/asaas/login/
```

### **3. Verificar static files:**

Abra o navegador, inspecione a página (F12) e veja se os arquivos CSS/JS estão carregando:
```
http://SEU_IP/asaas/static/custom.css
```

### **4. Fazer login e testar todas as páginas**

- Dashboard
- Clientes
- Recorrências
- Importação

---

## 🔄 Múltiplos Projetos no Mesmo Servidor

Você pode ter vários projetos:

### **Projeto 1 - Asaas Manager:**
```bash
cd /var/www/asaas
sudo bash deploy_vps_com_subdiretorio.sh
# Subdiretório: asaas
```

**Acesso:** `http://IP/asaas/`

### **Projeto 2 - Outro Sistema:**
```bash
cd /var/www/outro
sudo bash deploy_vps_com_subdiretorio.sh
# Subdiretório: outro
```

**Acesso:** `http://IP/outro/`

### **Cada um terá:**
- Socket próprio: `/run/gunicorn-asaas.sock`, `/run/gunicorn-outro.sock`
- Service próprio: `gunicorn-asaas`, `gunicorn-outro`
- Banco próprio: `asaas_db`, `outro_db`

---

## 🆘 Problemas Comuns

### **Página 404 ao acessar /asaas/**

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status gunicorn-asaas

# Ver logs
sudo journalctl -u gunicorn-asaas -n 50

# Restart
sudo systemctl restart gunicorn-asaas
```

### **Static files não carregam**

```bash
# Verificar FORCE_SCRIPT_NAME no .env
cat .env | grep FORCE_SCRIPT_NAME

# Coletar novamente
source venv/bin/activate
python manage.py collectstatic --noinput

# Verificar permissões
ls -la staticfiles/

# Restart Nginx
sudo systemctl restart nginx
```

### **Redireciona para URL errada**

Verifique se `FORCE_SCRIPT_NAME` está configurado:

```bash
cat .env | grep FORCE_SCRIPT_NAME
# Deve mostrar: FORCE_SCRIPT_NAME=/asaas
```

Se não estiver, adicione:

```bash
echo "FORCE_SCRIPT_NAME=/asaas" >> .env
sudo systemctl restart gunicorn-asaas
```

### **Erro 502 Bad Gateway**

```bash
# Verificar socket
ls -la /run/gunicorn-asaas.sock

# Se não existir, restart do Gunicorn
sudo systemctl restart gunicorn-asaas

# Ver erro específico
sudo journalctl -u gunicorn-asaas -f
```

---

## 🔧 Comandos Úteis

### **Ver logs:**
```bash
sudo journalctl -u gunicorn-asaas -f
```

### **Restart serviços:**
```bash
sudo systemctl restart gunicorn-asaas
sudo systemctl restart nginx
```

### **Ver status:**
```bash
sudo systemctl status gunicorn-asaas
sudo systemctl status nginx
```

### **Testar configuração do Nginx:**
```bash
sudo nginx -t
```

---

## 📊 Estrutura Final

```
http://IP/
├── /asaas/              <- Seu projeto
│   ├── /login/
│   ├── /clientes/
│   ├── /recorrencias/
│   └── /static/
│
├── /outro/              <- Outro projeto (opcional)
└── /site/               <- Outro site (opcional)
```

Cada projeto é independente:
- Banco de dados próprio
- Gunicorn próprio
- Static files próprios

---

## 🎯 Resumo

### **Vantagens:**
✅ Múltiplos projetos no mesmo IP  
✅ Cada projeto isolado  
✅ Fácil gerenciamento  
✅ Economiza recursos  

### **URL de acesso:**
```
http://SEU_IP/asaas/
```

### **Comando para deploy:**
```bash
sudo bash deploy_vps_com_subdiretorio.sh
```

---

## 🆙 Adicionar Domínio Depois

Quando tiver domínio, pode:

### **Opção 1: Subdomínio**
```
https://asaas.seudominio.com
```

### **Opção 2: Caminho**
```
https://seudominio.com/asaas/
```

Para configurar, execute:
```bash
sudo certbot --nginx -d seudominio.com
```

E atualize o `.env`:
```env
ALLOWED_HOSTS=seudominio.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

**Pronto! Sistema funcionando em subdiretório!** 🚀

Execute:
```bash
sudo bash deploy_vps_com_subdiretorio.sh
```

Acesse:
```
http://SEU_IP/asaas/
```

