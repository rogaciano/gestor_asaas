# 🔒 Proteção de Configurações do Servidor

Este documento explica como proteger as configurações do servidor para evitar que sejam sobrescritas durante atualizações do repositório.

## ⚠️ Arquivos que NUNCA devem ser commitados

Os seguintes arquivos estão protegidos no `.gitignore` e **NUNCA** serão commitados:

- `.env` - Arquivo de configuração com valores reais
- `.env.local` - Configurações locais
- `.env.production` - Configurações de produção
- `.env.staging` - Configurações de staging
- `db.sqlite3` - Banco de dados SQLite
- `logs/` - Arquivos de log
- `venv/` - Ambiente virtual Python

## 📋 Arquivos de Exemplo (podem ser commitados)

Estes arquivos são templates e **podem** ser commitados:

- `.env.example` - Template para desenvolvimento
- `.env.production.example` - Template para produção

## 🚀 Como atualizar o servidor sem perder configurações

### 1. Antes de fazer pull/atualização

```bash
# Verifique se seu .env está protegido
git status
# O arquivo .env NÃO deve aparecer na lista
```

### 2. Durante a atualização

```bash
# Faça o pull normalmente
git pull origin main

# O Git vai ignorar automaticamente o .env
# Suas configurações do servidor serão preservadas
```

### 3. Se precisar atualizar variáveis de ambiente

```bash
# Edite manualmente o .env no servidor
nano .env

# OU copie do exemplo e ajuste
cp .env.production.example .env
nano .env
```

## 📝 Variáveis de Ambiente Importantes

### Desenvolvimento
- `DEBUG=True` - Ativa modo debug
- `SECRET_KEY` - Chave secreta do Django
- `ASAAS_API_KEY` - Chave da API Asaas (sandbox)
- `ASAAS_API_URL=https://sandbox.asaas.com/api/v3`

### Produção
- `DEBUG=False` - **SEMPRE False em produção!**
- `SECRET_KEY` - Chave secreta única e segura
- `ASAAS_API_KEY` - Chave da API Asaas (produção)
- `ASAAS_API_URL=https://api.asaas.com/v3`
- `ALLOWED_HOSTS` - Lista de hosts permitidos
- `CSRF_TRUSTED_ORIGINS` - Origens confiáveis para CSRF
- `SESSION_COOKIE_SECURE=True` - Cookies seguros (HTTPS)
- `CSRF_COOKIE_SECURE=True` - Cookies CSRF seguros
- `SECURE_SSL_REDIRECT=True` - Redirecionar para HTTPS

### Banco de Dados (Produção)
- `DB_ENGINE=django.db.backends.postgresql`
- `DB_NAME` - Nome do banco
- `DB_USER` - Usuário do banco
- `DB_PASSWORD` - Senha do banco
- `DB_HOST` - Host do banco
- `DB_PORT` - Porta do banco

## 🔐 Boas Práticas

1. **Nunca commite o .env** - Sempre use `.env.example` como template
2. **Use valores diferentes** - Cada ambiente (dev, staging, prod) deve ter seu próprio .env
3. **Backup do .env** - Mantenha backup seguro do .env de produção
4. **Rotacione chaves** - Periodicamente, gere novas SECRET_KEY e API keys
5. **Verifique antes de pull** - Sempre verifique se o .env está protegido

## 🛠️ Scripts de Deploy

Os scripts de deploy (`deploy_vps.sh`, etc.) criam automaticamente o arquivo `.env` no servidor com valores seguros. Esses scripts:

- Geram uma SECRET_KEY única
- Configuram variáveis de produção
- Protegem o arquivo .env

**Importante:** Se você já tem um `.env` no servidor, o script de deploy **não vai sobrescrever** se você não permitir.

## 📞 Em caso de problemas

Se por acaso o `.env` for commitado acidentalmente:

```bash
# 1. Remova do histórico do Git (CUIDADO!)
git rm --cached .env
git commit -m "Remove .env do repositório"

# 2. Adicione ao .gitignore (já está lá, mas verifique)
echo ".env" >> .gitignore

# 3. Gere novas chaves no servidor (se necessário)
# Pois as chaves antigas podem estar expostas
```

## ✅ Checklist antes de fazer push

- [ ] `.env` não aparece em `git status`
- [ ] `.env.production` não aparece em `git status`
- [ ] `db.sqlite3` não aparece em `git status`
- [ ] Apenas arquivos de exemplo (`.env.example`) estão no commit
- [ ] Nenhuma senha ou token está no código fonte

---

**Lembre-se:** O `.gitignore` está configurado para proteger automaticamente seus arquivos sensíveis. Confie nele, mas sempre verifique antes de fazer commit!

