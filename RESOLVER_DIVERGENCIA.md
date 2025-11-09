# 🔄 Resolver Branches Divergentes no Servidor

Quando há branches divergentes, você pode escolher entre:
1. **Usar o código do GitHub** (ignorar mudanças do servidor) - Recomendado
2. **Mesclar as mudanças** (combinar servidor + GitHub)

## 🚀 Solução Rápida: Usar Código do GitHub

### Passo 1: Faça Backup do .env

```bash
# Backup do .env (IMPORTANTE!)
cp .env .env.backup
```

### Passo 2: Configure a Estratégia de Pull

```bash
# Configure para fazer merge (recomendado)
git config pull.rebase false
```

### Passo 3: Faça Reset para o Código do GitHub

```bash
# Descartar mudanças locais e usar código do GitHub
git fetch origin
git reset --hard origin/main
```

### Passo 4: Restaure o .env

```bash
# Restaure o .env do backup
cp .env.backup .env

# Verifique se está correto
cat .env | head -5
```

### Passo 5: Verifique

```bash
# Verifique o status
git status

# Deve mostrar "Your branch is up to date with 'origin/main'"
```

## 📋 Comandos Completos (Copie e Cole)

```bash
# 1. Backup do .env
cp .env .env.backup

# 2. Configure pull strategy
git config pull.rebase false

# 3. Faça reset para GitHub
git fetch origin
git reset --hard origin/main

# 4. Restaure .env
cp .env.backup .env

# 5. Verifique
git status
```

## ✅ Pronto!

Agora o servidor está sincronizado com o GitHub e seu `.env` foi preservado.

Para futuras atualizações:
```bash
git pull origin main
```

