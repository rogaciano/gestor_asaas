# Solução para Erro 500 Após Login no Servidor VPS

## 📋 Problema Identificado

Erro 500 após fazer login em: `http://144.202.29.245/gestor_asaas`

**Causa:** Configuração incorreta para deployment em subdiretório `/gestor_asaas`.

## ✅ Correções Aplicadas

### 1. Arquivos Modificados Localmente

- **`config/settings.py`**: 
  - Adicionado `SESSION_COOKIE_PATH` e `CSRF_COOKIE_PATH` para suportar subdiretório
  - Adicionado suporte a `CSRF_TRUSTED_ORIGINS`

### 2. Arquivos Criados

- **`.env.production.example`**: Exemplo de configuração para produção
- **`DEPLOY_VPS.md`**: Guia completo de deployment
- **`check_config.py`**: Script para verificar configuração
- **`SOLUCAO_ERRO_500.md`**: Este arquivo

## 🚀 Passos para Resolver no Servidor VPS

### Passo 1: Atualizar o Código no Servidor

```bash
# No servidor VPS
cd /caminho/para/gestor_asaas
git pull origin main  # ou rsync/scp os arquivos atualizados
```

### Passo 2: Editar o Arquivo `.env` no Servidor

Adicione/modifique estas linhas no `.env` do servidor VPS:

```bash
# CRÍTICO: Subdiretório
FORCE_SCRIPT_NAME=/gestor_asaas

# CRÍTICO: CSRF Origins
CSRF_TRUSTED_ORIGINS=http://144.202.29.245

# Hosts permitidos
ALLOWED_HOSTS=144.202.29.245,localhost,127.0.0.1

# Produção
DEBUG=False
```

### Passo 3: Verificar Configuração

```bash
# No servidor VPS
cd /caminho/para/gestor_asaas
source venv/bin/activate
python check_config.py
```

O script deve mostrar algo como:

```
✓ FORCE_SCRIPT_NAME: /gestor_asaas
✓ STATIC_URL: /gestor_asaas/static/
✓ SESSION_COOKIE_PATH: /gestor_asaas/
✓ CSRF_COOKIE_PATH: /gestor_asaas/
✓ CSRF_TRUSTED_ORIGINS: http://144.202.29.245
```

### Passo 4: Coletar Arquivos Estáticos

```bash
# No servidor VPS
python manage.py collectstatic --noinput
```

### Passo 5: Reiniciar o Servidor Web

#### Se usar Apache:
```bash
sudo systemctl restart apache2
```

#### Se usar Nginx + Gunicorn:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Passo 6: Testar

1. Acesse: `http://144.202.29.245/gestor_asaas/login/`
2. Faça login
3. Verifique se redireciona corretamente para: `http://144.202.29.245/gestor_asaas/`

## 🔍 Verificações Importantes

### Configuração do Apache (se aplicável)

O arquivo de configuração do Apache deve ter:

```apache
WSGIScriptAlias /gestor_asaas /caminho/para/gestor_asaas/config/wsgi.py
WSGIDaemonProcess gestor_asaas python-home=/caminho/para/venv python-path=/caminho/para/gestor_asaas
WSGIProcessGroup gestor_asaas

Alias /gestor_asaas/static /caminho/para/gestor_asaas/static
```

### Configuração do Nginx (se aplicável)

O arquivo de configuração do Nginx deve ter:

```nginx
location /gestor_asaas {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header SCRIPT_NAME /gestor_asaas;
}

location /gestor_asaas/static {
    alias /caminho/para/gestor_asaas/static;
}
```

## 🐛 Troubleshooting

### Ainda recebe erro 500?

1. **Habilite DEBUG temporariamente**:
   ```bash
   # No .env do servidor
   DEBUG=True
   ```
   
2. **Verifique os logs**:
   ```bash
   # Logs do Django
   tail -f /caminho/para/gestor_asaas/logs/security.log
   
   # Logs do Apache
   tail -f /var/log/apache2/error.log
   
   # Logs do Nginx
   tail -f /var/log/nginx/error.log
   ```

3. **Verifique permissões**:
   ```bash
   chmod -R 755 /caminho/para/gestor_asaas
   chown -R www-data:www-data /caminho/para/gestor_asaas  # Apache
   # ou
   chown -R nginx:nginx /caminho/para/gestor_asaas  # Nginx
   ```

### Erro 403 Forbidden?

- Limpe os cookies do navegador
- Verifique se `CSRF_TRUSTED_ORIGINS` está correto
- Certifique-se de que o protocolo (http/https) está correto no `CSRF_TRUSTED_ORIGINS`

### Arquivos CSS/JS não carregam?

- Execute `python manage.py collectstatic --noinput`
- Verifique a configuração do `Alias` no servidor web
- Verifique permissões da pasta `static`

## 📝 Resumo das Alterações

| Configuração | Valor Necessário |
|--------------|------------------|
| `FORCE_SCRIPT_NAME` | `/gestor_asaas` |
| `CSRF_TRUSTED_ORIGINS` | `http://144.202.29.245` |
| `ALLOWED_HOSTS` | `144.202.29.245,localhost` |
| `DEBUG` | `False` |
| `SESSION_COOKIE_PATH` | `/gestor_asaas/` (automático) |
| `CSRF_COOKIE_PATH` | `/gestor_asaas/` (automático) |

## 📞 Próximos Passos

Após aplicar as correções:

1. ✅ Faça upload dos arquivos atualizados para o servidor
2. ✅ Atualize o `.env` no servidor
3. ✅ Execute `check_config.py` para verificar
4. ✅ Colete os arquivos estáticos
5. ✅ Reinicie o servidor web
6. ✅ Teste o login

## 💡 Dica

Use o comando `python check_config.py` sempre que atualizar as configurações para garantir que tudo está correto!

---

**Criado em:** 07/11/2025  
**Servidor:** http://144.202.29.245/gestor_asaas
