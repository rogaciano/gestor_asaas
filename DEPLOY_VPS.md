# Guia de Deploy no Servidor VPS

## Problema Identificado
Erro 500 após login devido à configuração incorreta do subdiretório `/gestor_asaas`.

## Solução: Configurações Necessárias

### 1. Atualizar o arquivo `.env` no servidor VPS

No servidor VPS (144.202.29.245), edite o arquivo `.env` e adicione/modifique:

```bash
# IMPORTANTE: Configuração para subdiretório
FORCE_SCRIPT_NAME=/gestor_asaas

# Allowed Hosts
ALLOWED_HOSTS=144.202.29.245,localhost,127.0.0.1

# CSRF Trusted Origins (CRÍTICO para resolver erro 403/500)
CSRF_TRUSTED_ORIGINS=http://144.202.29.245

# Se estiver em produção
DEBUG=False
```

### 2. Verificar Configuração do Servidor Web

#### Se estiver usando Apache com mod_wsgi:

Verifique o arquivo de configuração do Apache (geralmente em `/etc/apache2/sites-available/`):

```apache
WSGIScriptAlias /gestor_asaas /caminho/para/gestor_asaas/config/wsgi.py
WSGIDaemonProcess gestor_asaas python-home=/caminho/para/venv python-path=/caminho/para/gestor_asaas
WSGIProcessGroup gestor_asaas

<Directory /caminho/para/gestor_asaas/config>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>

Alias /gestor_asaas/static /caminho/para/gestor_asaas/static
<Directory /caminho/para/gestor_asaas/static>
    Require all granted
</Directory>
```

#### Se estiver usando Nginx + Gunicorn:

Verifique o arquivo de configuração do Nginx:

```nginx
location /gestor_asaas {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header SCRIPT_NAME /gestor_asaas;
}

location /gestor_asaas/static {
    alias /caminho/para/gestor_asaas/static;
}
```

### 3. Coletar Arquivos Estáticos

No servidor VPS, execute:

```bash
cd /caminho/para/gestor_asaas
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 4. Reiniciar o Servidor Web

#### Apache:
```bash
sudo systemctl restart apache2
```

#### Nginx + Gunicorn:
```bash
sudo systemctl restart nginx
sudo systemctl restart gunicorn
```

### 5. Verificar Logs em Caso de Erro

#### Logs do Django:
```bash
tail -f /caminho/para/gestor_asaas/logs/security.log
```

#### Logs do Apache:
```bash
tail -f /var/log/apache2/error.log
```

#### Logs do Nginx:
```bash
tail -f /var/log/nginx/error.log
```

## Checklist de Verificação

- [ ] Arquivo `.env` atualizado com `FORCE_SCRIPT_NAME=/gestor_asaas`
- [ ] `CSRF_TRUSTED_ORIGINS` configurado corretamente
- [ ] `ALLOWED_HOSTS` contém o IP do servidor
- [ ] Configuração do servidor web (Apache/Nginx) atualizada
- [ ] Arquivos estáticos coletados (`collectstatic`)
- [ ] Servidor web reiniciado
- [ ] Acesso testado: http://144.202.29.245/gestor_asaas

## Testando a Solução

1. Acesse: http://144.202.29.245/gestor_asaas/login/
2. Faça login com suas credenciais
3. Verifique se o redirecionamento funciona corretamente

## Solução de Problemas

### Erro 500 ainda persiste?
1. Verifique os logs do Django: `tail -f logs/security.log`
2. Habilite temporariamente `DEBUG=True` no `.env` para ver o erro detalhado
3. Verifique permissões dos arquivos: `chmod -R 755 /caminho/para/gestor_asaas`

### Erro 403 Forbidden?
- Verifique se `CSRF_TRUSTED_ORIGINS` está configurado corretamente
- Limpe os cookies do navegador e tente novamente

### Arquivos estáticos não carregam?
- Verifique o caminho do `Alias` no servidor web
- Execute `python manage.py collectstatic` novamente
- Verifique permissões da pasta `static`

## Contato e Suporte

Se o problema persistir, forneça:
1. Mensagem de erro completa dos logs
2. Configuração do servidor web (Apache/Nginx)
3. Conteúdo do arquivo `.env` (sem senhas)
