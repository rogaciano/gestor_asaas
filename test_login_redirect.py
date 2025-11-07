#!/usr/bin/env python
"""
Script para testar o redirecionamento após login
Execute: python test_login_redirect.py
"""
import os
import sys
from pathlib import Path

# Adiciona o projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Carrega as configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    from django.urls import reverse
    from django.test import RequestFactory, Client
    
    print("\n" + "="*60)
    print("TESTE DE REDIRECIONAMENTO APÓS LOGIN")
    print("="*60)
    
    # Testar geração de URLs
    print(f"\n✓ FORCE_SCRIPT_NAME: {settings.FORCE_SCRIPT_NAME or '(não configurado)'}")
    
    print("\n" + "-"*60)
    print("URLs GERADAS:")
    print("-"*60)
    
    urls_to_test = [
        ('login', 'URL de Login'),
        ('home', 'URL de Home'),
        ('cliente_list', 'URL de Clientes'),
        ('recorrencia_list', 'URL de Recorrências'),
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✓ {description:25s} -> {url}")
        except Exception as e:
            print(f"✗ {description:25s} -> ERRO: {e}")
    
    # Testar login com o Client do Django
    print("\n" + "-"*60)
    print("TESTE DE LOGIN E REDIRECIONAMENTO:")
    print("-"*60)
    
    client = Client()
    
    # 1. Acessar página de login
    response = client.get(reverse('login'))
    print(f"\n1. GET /login/")
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.request.get('PATH_INFO', 'N/A')}")
    
    # 2. Fazer login
    from django.contrib.auth.models import User
    users = User.objects.filter(is_superuser=True)
    
    if users.exists():
        test_user = users.first()
        print(f"\n2. Testando login com usuário: {test_user.username}")
        
        # Note: Não podemos testar com senha real aqui, apenas estrutura
        print(f"   ⚠ Para testar login real, use o navegador")
        print(f"   URL de login: {reverse('login')}")
        print(f"   URL esperada após login: {reverse('home')}")
        
    else:
        print("\n⚠ Nenhum superusuário encontrado para teste")
    
    # 3. Verificar configuração de cookies
    print("\n" + "-"*60)
    print("CONFIGURAÇÃO DE COOKIES:")
    print("-"*60)
    print(f"✓ SESSION_COOKIE_PATH: {settings.SESSION_COOKIE_PATH}")
    print(f"✓ CSRF_COOKIE_PATH: {settings.CSRF_COOKIE_PATH}")
    
    if settings.FORCE_SCRIPT_NAME:
        if not settings.SESSION_COOKIE_PATH.startswith(settings.FORCE_SCRIPT_NAME):
            print("  ⚠ ATENÇÃO: SESSION_COOKIE_PATH não corresponde ao FORCE_SCRIPT_NAME")
        else:
            print("  ✓ Configuração de cookies está correta")
    
    # 4. Verificar settings de login
    print("\n" + "-"*60)
    print("CONFIGURAÇÕES DE LOGIN:")
    print("-"*60)
    print(f"✓ LOGIN_URL: {settings.LOGIN_URL}")
    print(f"✓ LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
    print(f"✓ LOGOUT_REDIRECT_URL: {settings.LOGOUT_REDIRECT_URL}")
    
    # Tentar resolver os nomes
    try:
        login_redirect_resolved = reverse(settings.LOGIN_REDIRECT_URL)
        print(f"✓ LOGIN_REDIRECT_URL resolvida: {login_redirect_resolved}")
    except:
        print(f"⚠ LOGIN_REDIRECT_URL não pôde ser resolvida como nome de URL")
    
    print("\n" + "="*60)
    print("DIAGNÓSTICO:")
    print("="*60)
    
    issues = []
    
    if settings.FORCE_SCRIPT_NAME:
        print(f"\n✓ Aplicação configurada para subdiretório: {settings.FORCE_SCRIPT_NAME}")
        
        home_url = reverse('home')
        if not home_url.startswith(settings.FORCE_SCRIPT_NAME):
            issues.append(f"URL home não inclui o FORCE_SCRIPT_NAME")
            issues.append(f"  Esperado: {settings.FORCE_SCRIPT_NAME}/")
            issues.append(f"  Obtido: {home_url}")
    else:
        print("\n✓ Aplicação configurada para rodar na raiz")
    
    if issues:
        print("\n⚠ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ Nenhum problema encontrado na configuração")
    
    print("\n" + "="*60)
    print("RECOMENDAÇÕES:")
    print("="*60)
    
    print("\n1. No servidor VPS, verifique o arquivo .env:")
    print("   FORCE_SCRIPT_NAME=/gestor_asaas")
    
    print("\n2. Verifique a configuração do servidor web (Apache/Nginx)")
    print("   Deve estar configurado para servir em /gestor_asaas")
    
    print("\n3. Limpe os cookies do navegador antes de testar")
    
    print("\n4. Monitore os logs durante o login:")
    print("   tail -f logs/security.log")
    
    print("\n" + "="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
