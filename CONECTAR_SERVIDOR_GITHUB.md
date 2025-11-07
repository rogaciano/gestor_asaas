# 🔗 Conectar Servidor ao GitHub

Este guia mostra como conectar o projeto que já está configurado no servidor ao repositório GitHub.

## 📋 Situação Atual

Você já tem:
- ✅ Projeto configurado e funcionando no servidor
- ✅ Arquivo `.env` com configurações do servidor
- ✅ Repositório GitHub criado: `https://github.com/rogaciano/gestor_asaas`

## 🚀 Passo a Passo

### 1. Acesse o Servidor

```bash
ssh usuario@seu-servidor
cd /caminho/para/gestor_asaas
```

### 2. Verifique se já existe repositório Git

```bash
# Verifique se já é um repositório Git
git status
```

**Se NÃO for um repositório Git ainda:**

```bash
# Inicialize o repositório
git init
git branch -M main
```

**Se JÁ for um repositório Git:**

```bash
# Verifique o remote atual
git remote -v
```

### 3. Configure o Remote do GitHub

**Se não houver remote configurado:**

```bash
# Adicione o remote do GitHub
git remote add origin https://github.com/rogaciano/gestor_asaas.git
```

**Se já houver um remote diferente:**

```bash
# Remova o remote antigo (se necessário)
git remote remove origin

# Adicione o novo remote
git remote add origin https://github.com/rogaciano/gestor_asaas.git
```

**Ou atualize o remote existente:**

```bash
git remote set-url origin https://github.com/rogaciano/gestor_asaas.git
```

### 4. Verifique o Status

```bash
# Veja o status atual
git status

# Verifique o remote
git remote -v
```

### 5. Proteja o .env (IMPORTANTE!)

```bash
# Verifique se o .env está no .gitignore
cat .gitignore | grep "\.env"

# Se não estiver, adicione manualmente
echo ".env" >> .gitignore
echo ".env.production" >> .gitignore
echo ".env.local" >> .gitignore
```

### 6. Adicione e Faça Commit dos Arquivos

```bash
# Adicione todos os arquivos (o .env será ignorado automaticamente)
git add .

# Verifique o que será commitado (o .env NÃO deve aparecer!)
git status

# Faça o commit inicial
git commit -m "Configuração inicial do servidor"
```

### 7. Sincronize com o GitHub

**Opção A: Se o servidor tem código que não está no GitHub**

```bash
# Faça pull primeiro para ver se há conflitos
git pull origin main --allow-unrelated-histories

# Se houver conflitos, resolva manualmente
# Depois faça push
git push -u origin main
```

**Opção B: Se o servidor está vazio ou quer sobrescrever**

```bash
# Faça pull do GitHub (isso vai trazer todo o código)
git pull origin main --allow-unrelated-histories

# Seu .env será preservado (está no .gitignore)
```

**Opção C: Se quer manter o código do servidor e mesclar**

```bash
# 1. Faça backup do código atual
cp -r . ../gestor_asaas_backup

# 2. Faça pull
git pull origin main --allow-unrelated-histories

# 3. Se houver conflitos, resolva manualmente
# 4. Faça commit das mudanças
git add .
git commit -m "Mescla configuração servidor com GitHub"

# 5. Faça push
git push origin main
```

### 8. Verifique se Está Sincronizado

```bash
# Veja o status
git status

# Veja o histórico
git log --oneline -5

# Verifique o remote
git remote -v
```

## 🔄 Atualizações Futuras

Depois de conectar, para atualizar o servidor:

```bash
cd /caminho/para/gestor_asaas
git pull origin main
```

O `.env` será preservado automaticamente!

## ⚠️ Problemas Comuns

### Erro: "fatal: refusing to merge unrelated histories"

```bash
# Use a flag --allow-unrelated-histories
git pull origin main --allow-unrelated-histories
```

### Erro: "Your local changes would be overwritten"

```bash
# Faça backup das mudanças locais
git stash

# Faça o pull
git pull origin main

# Restaure as mudanças (se necessário)
git stash pop
```

### O .env aparece no git status

```bash
# Remova do índice (mas mantenha o arquivo)
git rm --cached .env

# Adicione ao .gitignore
echo ".env" >> .gitignore

# Faça commit
git add .gitignore
git commit -m "Remove .env do repositório"
```

### Conflitos de merge

```bash
# Veja os arquivos em conflito
git status

# Resolva manualmente cada arquivo
# Depois:
git add .
git commit -m "Resolve conflitos"
```

## 🔐 Autenticação no GitHub

### Opção 1: HTTPS (Recomendado - mais simples)

```bash
# Use token de acesso pessoal
git remote set-url origin https://SEU_TOKEN@github.com/rogaciano/gestor_asaas.git
```

**Como criar token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Selecione permissões: `repo`
4. Copie o token e use no comando acima

### Opção 2: SSH (Mais seguro)

```bash
# Gere chave SSH no servidor
ssh-keygen -t ed25519 -C "servidor@gestor_asaas"

# Copie a chave pública
cat ~/.ssh/id_ed25519.pub

# Adicione no GitHub: Settings → SSH and GPG keys → New SSH key

# Configure o remote para usar SSH
git remote set-url origin git@github.com:rogaciano/gestor_asaas.git
```

## ✅ Checklist de Conexão

- [ ] Acessei o servidor via SSH
- [ ] Naveguei até o diretório do projeto
- [ ] Verifiquei se é repositório Git (ou inicializei)
- [ ] Configurei o remote do GitHub
- [ ] Verifiquei que `.env` está no `.gitignore`
- [ ] Fiz commit dos arquivos (sem o .env)
- [ ] Sincronizei com o GitHub (pull/push)
- [ ] Testei atualização (`git pull origin main`)
- [ ] Verifiquei que `.env` foi preservado

## 📝 Exemplo Completo

```bash
# 1. Acesse o servidor
ssh usuario@192.168.1.100
cd /var/www/gestor_asaas

# 2. Configure Git (se necessário)
git init
git branch -M main

# 3. Configure remote
git remote add origin https://github.com/rogaciano/gestor_asaas.git

# 4. Verifique .gitignore
echo ".env" >> .gitignore

# 5. Adicione arquivos
git add .
git status  # Verifique que .env NÃO aparece

# 6. Commit
git commit -m "Configuração inicial servidor"

# 7. Sincronize
git pull origin main --allow-unrelated-histories

# 8. Teste atualização
git pull origin main
cat .env  # Deve estar intacto!
```

---

**Pronto!** Agora seu servidor está conectado ao GitHub e você pode atualizar com `git pull origin main` sem perder as configurações!

