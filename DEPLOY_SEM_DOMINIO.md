# 🚀 Deploy na VPS SEM Domínio (Acesso via IP)

## ✅ Sem problema! Você pode usar o IP da VPS

---

## ⚡ Deploy Rápido (Recomendado)

### **Comando único:**

```bash
sudo bash deploy_vps_sem_dominio.sh
```

**Pronto!** O script faz tudo automaticamente! 🎉

---

## 📋 Durante o processo você vai precisar:

1. **Nome do banco** (ou deixe em branco para `asaas_db`)
2. **Usuário do banco** (ou deixe em branco para `asaas_user`)
3. **Senha do banco** (deixe em branco para gerar automaticamente)
4. **API Key do Asaas** (produção)
5. **Criar usuário admin** (username, email, senha)

**NÃO precisa fornecer domínio!** O script detecta o IP automaticamente.

---

## 🌐 Como Acessar

Após o deploy, acesse:

```
http://SEU_IP_DA_VPS/login/
```

**Exemplo:**
```
http://123.456.789.012/login/
```

---

## ⚠️ Diferenças do Deploy com Domínio

### **SEM Domínio (IP):**
- ✅ Acesso via IP
- ⚠️ HTTP (não HTTPS)
- ⚠️ Sem certificado SSL
- ⚠️ Navegador mostra "Não seguro"

### **COM Domínio:**
- ✅ Acesso via domínio
- ✅ HTTPS (seguro)
- ✅ Certificado SSL
- ✅ Cadeado verde no navegador

---

## 🔒 Sobre Segurança

### **É seguro usar sem domínio?**

**Para desenvolvimento/testes:** ✅ Sim  
**Para produção:** ⚠️ Recomendado ter domínio e SSL

### **O que funciona normalmente:**
- ✅ Login/logout
- ✅ Todas as funcionalidades
- ✅ Integração com Asaas (API usa HTTPS)
- ✅ Banco de dados seguro
- ✅ Sessões funcionam

### **O que NÃO tem sem SSL:**
- ❌ Criptografia HTTPS
- ❌ Cookies "Secure"
- ❌ Cadeado verde no navegador

---

## 🎯 Configurações Automáticas

O script configura automaticamente:

```env
# .env gerado automaticamente
DEBUG=False
ALLOWED_HOSTS=123.456.789.012

# Segurança adaptada para HTTP
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
```

**Tudo otimizado para funcionar via IP!**

---

## 📝 Passo a Passo Manual

Se preferir fazer manualmente:

### **1. Tornar script executável**
```bash
chmod +x deploy_vps_sem_dominio.sh
```

### **2. Executar como root**
```bash
sudo bash deploy_vps_sem_dominio.sh
```

### **3. Aguardar conclusão**

O script mostrará o IP no final:
```
🌐 URL do Sistema:
   http://123.456.789.012
```

### **4. Acessar o sistema**
```
http://SEU_IP/login/
```

---

## 🔧 Comandos Úteis

### **Ver IP da VPS:**
```bash
curl ifconfig.me
```

### **Ver status dos serviços:**
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### **Ver logs:**
```bash
# Logs do Gunicorn
sudo journalctl -u gunicorn -f

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log
```

### **Reiniciar serviços:**
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 🆙 Adicionar Domínio Depois

Quando você tiver um domínio, pode adicionar SSL facilmente:

### **Passo 1: Apontar domínio para o IP**

No painel do seu provedor de domínio:
```
Tipo: A
Nome: @
Valor: 123.456.789.012
TTL: 3600
```

### **Passo 2: Atualizar Nginx**

```bash
sudo nano /etc/nginx/sites-available/asaas_manager
```

Altere:
```nginx
server_name 123.456.789.012;
```

Para:
```nginx
server_name seudominio.com www.seudominio.com;
```

### **Passo 3: Instalar SSL**

```bash
sudo certbot --nginx -d seudominio.com -d www.seudominio.com
```

### **Passo 4: Atualizar .env**

```bash
nano .env
```

Altere:
```env
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

### **Passo 5: Restart**

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

**Pronto! Agora com HTTPS!** 🔐

---

## ✅ Checklist

Antes de executar:

- [ ] Está na pasta do projeto na VPS
- [ ] Tem acesso root (sudo)
- [ ] Tem API Key de produção do Asaas
- [ ] Anotou o IP da VPS

Após executar:

- [ ] Acessa via http://IP/login/
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Pode criar clientes
- [ ] Pode criar recorrências

---

## 🆘 Problemas Comuns

### **Não consigo acessar o IP**

```bash
# Verificar se Nginx está rodando
sudo systemctl status nginx

# Verificar firewall
sudo ufw status

# Permitir HTTP
sudo ufw allow 'Nginx HTTP'
```

### **Página não carrega**

```bash
# Ver logs do Gunicorn
sudo journalctl -u gunicorn -n 50

# Restart
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### **Erro 502**

```bash
# Verificar socket do Gunicorn
ls -la /run/gunicorn.sock

# Restart do Gunicorn
sudo systemctl restart gunicorn
```

---

## 📊 Resumo

### **O Que Você Terá:**

✅ Sistema funcionando 100%  
✅ Acesso via IP  
✅ PostgreSQL configurado  
✅ Gunicorn rodando  
✅ Nginx configurado  
✅ Firewall ativo  
✅ Todas as funcionalidades operacionais  

### **O Que NÃO Terá (por enquanto):**

⚠️ HTTPS  
⚠️ Certificado SSL  
⚠️ Cadeado verde  

**Mas isso pode ser adicionado depois quando tiver domínio!**

---

## 🎉 Pronto para Começar?

Execute o comando:

```bash
sudo bash deploy_vps_sem_dominio.sh
```

Após a conclusão, acesse:

```
http://SEU_IP/login/
```

---

## 💡 Dicas

### **Para uso temporário:**
- IP funciona perfeitamente
- Ideal para testes e desenvolvimento
- Todas as funcionalidades disponíveis

### **Para produção:**
- Recomendo adquirir um domínio
- Domínios .com custam ~R$40/ano
- Com domínio você terá HTTPS gratuito

### **Provedores de domínio baratos:**
- Registro.br (.br) - R$40/ano
- Namecheap (.com) - ~R$50/ano
- Hostinger - ~R$40/ano

---

**Sistema pronto via IP!** 🚀

Quando tiver domínio, volte aqui na seção "Adicionar Domínio Depois" para adicionar SSL!

