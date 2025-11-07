# 🚀 Como Atualizar o Código no Servidor

Este guia mostra os comandos Git para atualizar o código no servidor sem perder as configurações.

## 📋 Comandos Básicos

### 1. Atualização Simples (Recomendado)

```bash
# Navegue até o diretório do projeto
cd /caminho/para/gestor_asaas

# Atualize o código do repositório
git pull origin main
```

### 2. Atualização com Verificação

```bash
# 1. Verifique o status atual
git status

# 2. Veja as mudanças que serão aplicadas
git fetch origin main
git log HEAD..origin/main

# 3. Faça o pull
git pull origin main
```

### 3. Atualização Forçada (se necessário)

⚠️ **Use apenas se houver conflitos e você tiver certeza:**

```bash
# Backup primeiro!
cp -r . /backup/gestor_asaas_$(date +%Y%m%d_%H%M%S)

# Atualize forçando (sobrescreve mudanças locais)
git fetch origin
git reset --hard origin/main
```

## 🔒 Proteção Automática

O `.gitignore` protege automaticamente:
- ✅ Seu arquivo `.env` **NÃO será sobrescrito**
- ✅ Configurações do servidor **serão preservadas**
- ✅ Apenas código fonte será atualizado

## 📝 Passo a Passo Completo

### Antes de Atualizar

```bash
# 1. Verifique se está na branch correta
git branch

# 2. Verifique se há mudanças locais não commitadas
git status

# 3. Se houver mudanças locais, faça backup
git stash save "backup antes de atualizar"
```

### Durante a Atualização

```bash
# 4. Atualize o código
git pull origin main

# 5. Se houver conflitos, resolva manualmente
# (geralmente não haverá, pois .env está protegido)
```

### Depois de Atualizar

```bash
# 6. Se necessário, reinstale dependências
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# 7. Execute migrações (se houver novas)
python manage.py migrate

# 8. Colete arquivos estáticos (se necessário)
python manage.py collectstatic --noinput

# 9. Reinicie o servidor (se usar systemd/supervisor)
sudo systemctl restart gestor_asaas
# OU
sudo supervisorctl restart gestor_asaas
```

## 🔄 Script de Atualização Automática

Crie um script `atualizar.sh` no servidor:

```bash
#!/bin/bash
# Script de atualização do Gestor Asaas

set -e  # Para em caso de erro

echo "🔄 Atualizando Gestor Asaas..."

# Diretório do projeto
cd /caminho/para/gestor_asaas

# Ativa ambiente virtual
source venv/bin/activate

# Atualiza código
echo "📥 Baixando atualizações..."
git pull origin main

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt --quiet

# Executa migrações
echo "🗄️  Executando migrações..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Reinicia serviço
echo "🔄 Reiniciando serviço..."
sudo systemctl restart gestor_asaas

echo "✅ Atualização concluída!"
```

Torne o script executável:
```bash
chmod +x atualizar.sh
```

Execute:
```bash
./atualizar.sh
```

## ⚠️ Situações Especiais

### Se o repositório não estiver configurado

```bash
# Configure o remote
git remote add origin https://github.com/rogaciano/gestor_asaas.git

# Ou atualize se já existir
git remote set-url origin https://github.com/rogaciano/gestor_asaas.git
```

### Se houver conflitos no .env

```bash
# O .env está protegido, mas se houver problema:
# 1. Faça backup
cp .env .env.backup

# 2. Restaure do backup se necessário
cp .env.backup .env
```

### Se precisar atualizar apenas arquivos específicos

```bash
# Atualize apenas um arquivo específico
git fetch origin main
git checkout origin/main -- caminho/do/arquivo.py
```

## 🔍 Verificação Pós-Atualização

```bash
# Verifique se o .env ainda está intacto
cat .env | grep SECRET_KEY

# Verifique se o servidor está rodando
sudo systemctl status gestor_asaas

# Verifique os logs
tail -f logs/security.log
```

## 📞 Comandos Úteis

```bash
# Ver histórico de commits
git log --oneline -10

# Ver diferenças entre local e remoto
git diff HEAD origin/main

# Verificar status
git status

# Ver configuração do remote
git remote -v

# Ver branch atual
git branch
```

## ✅ Checklist de Atualização

- [ ] Backup do `.env` (opcional, mas recomendado)
- [ ] Verificar status do Git (`git status`)
- [ ] Fazer pull (`git pull origin main`)
- [ ] Instalar dependências se necessário (`pip install -r requirements.txt`)
- [ ] Executar migrações se necessário (`python manage.py migrate`)
- [ ] Coletar arquivos estáticos se necessário (`python manage.py collectstatic`)
- [ ] Reiniciar serviço se necessário
- [ ] Verificar se o sistema está funcionando

---

**Lembre-se:** O `.env` está protegido pelo `.gitignore` e **não será sobrescrito** durante o `git pull`!

