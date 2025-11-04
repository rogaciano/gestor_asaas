# ⚡ Deploy Rápido na VPS

## Você está na pasta do projeto na VPS? Perfeito!

Siga estes passos:

---

## 🚀 Opção 1: Script Automático (Mais Rápido)

### **Passo Único:**

```bash
sudo bash deploy_vps.sh
```

**O script vai:**
1. Instalar todas as dependências
2. Configurar PostgreSQL
3. Configurar ambiente virtual
4. Configurar Nginx
5. Configurar SSL (HTTPS)
6. Configurar Firewall
7. Tudo pronto! 🎉

**Durante o processo você vai precisar fornecer:**
- Domínio da VPS (ex: seusite.com)
- API Key do Asaas (produção)
- Criar usuário admin

**Tempo estimado:** 5-10 minutos

---

## 📝 Opção 2: Passo a Passo Manual

### **1. Tornar script executável**
```bash
chmod +x deploy_vps.sh
```

### **2. Executar como root**
```bash
sudo bash deploy_vps.sh
```

### **3. Responder as perguntas:**

- **Nome do banco:** asaas_db (ou deixe em branco)
- **Usuário do banco:** asaas_user (ou deixe em branco)
- **Senha do banco:** deixe em branco para gerar automaticamente
- **Domínio:** seudominio.com
- **API Key:** sua chave de produção do Asaas

### **4. Criar usuário admin quando solicitado:**

```
Username: admin
Email: seu@email.com
Password: ********
```

### **5. Aguardar conclusão**

O script mostrará todas as informações importantes no final!

---

## ✅ Após o Deploy

### **Acessar o sistema:**
```
https://seudominio.com/login/
```

### **Fazer login:**
Use o usuário admin que você criou

### **Verificar se está funcionando:**
- [ ] HTTPS funciona (cadeado verde)
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Pode criar clientes
- [ ] Pode criar recorrências

---

## 🔧 Comandos Úteis Após Deploy

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

### **Restart dos serviços:**
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 📊 Informações Importantes

**O script salva automaticamente:**
- Senha do banco de dados
- SECRET_KEY
- Todas as configurações

**Anote essas informações quando aparecerem no final!**

---

## 🆘 Problemas?

### **Script não executa:**
```bash
# Verificar permissões
ls -la deploy_vps.sh

# Dar permissão
chmod +x deploy_vps.sh

# Executar como root
sudo bash deploy_vps.sh
```

### **Erro durante execução:**
```bash
# Ver últimas linhas do log
sudo journalctl -u gunicorn -n 50

# Verificar sintaxe do Nginx
sudo nginx -t
```

### **Site não abre:**
```bash
# Verificar se serviços estão rodando
sudo systemctl status gunicorn
sudo systemctl status nginx

# Ver IP da VPS
curl ifconfig.me

# Verificar DNS
nslookup seudominio.com
```

---

## 📋 Checklist Rápido

Antes de executar o script, certifique-se de que:

- [ ] Está dentro da pasta do projeto
- [ ] Tem acesso root (sudo)
- [ ] Domínio está apontando para o IP da VPS
- [ ] Tem a API Key de produção do Asaas
- [ ] Backup do projeto local está feito

---

## 🎯 Resumo do Que o Script Faz

1. ✅ Atualiza o sistema
2. ✅ Instala Python, PostgreSQL, Nginx
3. ✅ Configura banco de dados
4. ✅ Cria ambiente virtual
5. ✅ Instala dependências
6. ✅ Configura .env
7. ✅ Executa migrations
8. ✅ Coleta static files
9. ✅ Cria superusuário
10. ✅ Configura Gunicorn
11. ✅ Configura Nginx
12. ✅ Instala SSL (HTTPS)
13. ✅ Configura Firewall
14. ✅ Sistema no ar!

---

## 🎉 Pronto!

Após executar o script, seu sistema estará:
- ✅ Rodando em HTTPS
- ✅ Com banco PostgreSQL
- ✅ Protegido por firewall
- ✅ Com certificado SSL válido
- ✅ Pronto para uso!

**Acesse:** https://seudominio.com/login/

---

**Dúvidas?** Consulte o [DEPLOY_VPS_GUIA.md](DEPLOY_VPS_GUIA.md) completo!

