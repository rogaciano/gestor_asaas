# Solução: Login Autentica mas Não Redireciona

## 🐛 Problema

Após fazer login com usuário e senha corretos:
- ✅ Mensagem "Bem-vindo, admin!" aparece
- ❌ Não redireciona para a página home
- Fica travado na tela de login

## 🔍 Causa Raiz

O problema ocorre quando `FORCE_SCRIPT_NAME=/gestor_asaas` está configurado, mas:
1. Os cookies de sessão não estão no path correto
2. O redirect não está gerando a URL completa com o subdiretório
3. O servidor web pode estar interferindo no redirecionamento

## ✅ Soluções Aplicadas

### 1. View de Login Corrigida

**Arquivo:** `asaas_app/views.py`

**Mudança:** Usar `reverse()` para gerar URLs corretas

```python
# ANTES
return redirect('home')

# DEPOIS
return redirect(reverse('home'))
```

Isso garante que o Django gere a URL correta incluindo o `FORCE_SCRIPT_NAME`.

### 2. Configuração de Cookies (já aplicado anteriormente)

**Arquivo:** `config/settings.py`

```python
if FORCE_SCRIPT_NAME:
    STATIC_URL = FORCE_SCRIPT_NAME + '/static/'
    SESSION_COOKIE_PATH = FORCE_SCRIPT_NAME + '/'
    CSRF_COOKIE_PATH = FORCE_SCRIPT_NAME + '/'
else:
    STATIC_URL = 'static/'
    SESSION_COOKIE_PATH = '/'
    CSRF_COOKIE_PATH = '/'
```

## 🚀 Passos para Resolver no Servidor VPS

### Passo 1: Atualizar Código no Servidor

```bash
cd /caminho/para/gestor_asaas
git pull origin main
# ou copie os arquivos atualizados via scp/rsync
```

### Passo 2: Verificar .env no Servidor

Certifique-se que o arquivo `.env` no servidor VPS contém:

```bash
FORCE_SCRIPT_NAME=/gestor_asaas
CSRF_TRUSTED_ORIGINS=http://144.202.29.245
ALLOWED_HOSTS=144.202.29.245,localhost,127.0.0.1
DEBUG=False
```

### Passo 3: Verificar Configuração do Servidor Web

#### Para Apache + mod_wsgi:

Arquivo: `/etc/apache2/sites-available/gestor_asaas.conf`

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

# IMPORTANTE: Preservar Headers para o Django
WSGIPassAuthorization On
```

#### Para Nginx + Gunicorn:

Arquivo: `/etc/nginx/sites-available/gestor_asaas`

```nginx
location /gestor_asaas {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # IMPORTANTE: Informar ao Django sobre o subdiretório
    proxy_set_header SCRIPT_NAME /gestor_asaas;
    
    # IMPORTANTE: Permitir redirects
    proxy_redirect off;
}

location /gestor_asaas/static {
    alias /caminho/para/gestor_asaas/static;
}
```

**Importante:** O `proxy_redirect off;` é crítico para permitir que o Django gerencie seus próprios redirects.

### Passo 4: Limpar Cookies do Navegador

**MUITO IMPORTANTE:** Cookies antigos com path errado podem causar esse problema!

1. Abra as Ferramentas do Desenvolvedor (F12)
2. Vá em Application > Cookies
3. Delete todos os cookies do domínio `144.202.29.245`
4. Ou use navegação anônima para testar

### Passo 5: Reiniciar Serviços

```bash
# Apache
sudo systemctl restart apache2

# Nginx + Gunicorn
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Verificar status
sudo systemctl status apache2  # ou nginx
```

### Passo 6: Testar com Logs Ativos

Terminal 1 - Logs do Django:
```bash
tail -f /caminho/para/gestor_asaas/logs/security.log
```

Terminal 2 - Logs do Servidor Web:
```bash
# Apache
tail -f /var/log/apache2/error.log

# Nginx
tail -f /var/log/nginx/error.log
```

Faça o login e observe os logs. Você deve ver:
```
Login successful for admin, redirecting to: /gestor_asaas/
```

## 🧪 Testes para Validar

### Teste 1: Verificar URLs Geradas

No servidor VPS:
```bash
cd /caminho/para/gestor_asaas
source venv/bin/activate
python test_login_redirect.py
```

Deve mostrar:
```
✓ URL de Home -> /gestor_asaas/
✓ SESSION_COOKIE_PATH: /gestor_asaas/
```

### Teste 2: Teste Manual de Login

1. Acesse: `http://144.202.29.245/gestor_asaas/login/`
2. Limpe os cookies (F12 > Application > Clear storage)
3. Digite usuário e senha
4. Clique em "Entrar"
5. Observe a barra de endereço

**Resultado esperado:**
- URL muda para: `http://144.202.29.245/gestor_asaas/`
- Página home carrega
- Menu de navegação aparece

### Teste 3: Verificar Headers HTTP

Use curl para testar:
```bash
curl -i -X POST \
  http://144.202.29.245/gestor_asaas/login/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=SENHA&csrfmiddlewaretoken=TOKEN'
```

Procure por:
```
HTTP/1.1 302 Found
Location: /gestor_asaas/
```

## 🔍 Troubleshooting

### Problema: Cookies não estão sendo salvos

**Sintoma:** Mesmo após login, ainda aparece como não autenticado

**Solução:**
1. Verifique que `SESSION_COOKIE_PATH` está correto
2. Verifique que `CSRF_TRUSTED_ORIGINS` inclui o domínio correto
3. Limpe todos os cookies antigos

### Problema: Redirect leva para URL errada

**Sintoma:** Redireciona para `http://144.202.29.245/` em vez de `/gestor_asaas/`

**Solução:**
1. Verifique que `FORCE_SCRIPT_NAME=/gestor_asaas` está no `.env`
2. Reinicie o servidor web após alterar `.env`
3. No Nginx, adicione `proxy_set_header SCRIPT_NAME /gestor_asaas;`

### Problema: Erro 404 após redirect

**Sintoma:** Redireciona mas dá erro 404

**Solução:**
1. Verifique configuração do servidor web
2. Certifique-se que a rota `/gestor_asaas/` está configurada
3. Verifique permissões dos arquivos

### Problema: Mensagem aparece mas não some

**Sintoma:** "Bem-vindo" fica aparecendo, página não muda

**Solução JavaScript:**

Adicione este código no template de login (se necessário):

```html
<!-- No final de auth/login.html, antes de </body> -->
<script>
    // Forçar redirect se houver mensagem de sucesso
    document.addEventListener('DOMContentLoaded', function() {
        const successMessage = document.querySelector('.bg-green-50');
        if (successMessage) {
            setTimeout(function() {
                window.location.href = "{{ url 'home' }}";
            }, 1000);
        }
    });
</script>
```

## 📊 Checklist Final

Antes de testar, certifique-se:

- [ ] `.env` do servidor tem `FORCE_SCRIPT_NAME=/gestor_asaas`
- [ ] `.env` do servidor tem `CSRF_TRUSTED_ORIGINS=http://144.202.29.245`
- [ ] Código atualizado no servidor (com `reverse()` no login)
- [ ] Configuração do servidor web correta (WSGIScriptAlias ou proxy_pass)
- [ ] Headers do servidor web configurados (SCRIPT_NAME, etc.)
- [ ] Servidor web reiniciado
- [ ] Cookies do navegador limpos
- [ ] Teste em navegação anônima

## 📝 Resumo das Mudanças

| Arquivo | Mudança | Motivo |
|---------|---------|--------|
| `asaas_app/views.py` | `redirect(reverse('home'))` | Gerar URL correta com FORCE_SCRIPT_NAME |
| `config/settings.py` | SESSION_COOKIE_PATH e CSRF_COOKIE_PATH | Cookies no path correto |
| Servidor Web | Headers SCRIPT_NAME | Django saber o subdiretório |
| `.env` | FORCE_SCRIPT_NAME e CSRF_TRUSTED_ORIGINS | Configuração base |

## 🎯 Resultado Esperado

Após aplicar todas as correções:

1. ✅ Acessa `http://144.202.29.245/gestor_asaas/login/`
2. ✅ Digita usuário e senha
3. ✅ Vê mensagem "Bem-vindo, admin!"
4. ✅ **É imediatamente redirecionado para** `http://144.202.29.245/gestor_asaas/`
5. ✅ Vê a página home com dashboard
6. ✅ Menu de navegação funciona

---

**Data:** 07/11/2025  
**Servidor:** http://144.202.29.245/gestor_asaas  
**Status:** ✅ Corrigido - Pronto para aplicar no servidor
