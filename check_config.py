#!/usr/bin/env python
"""
Script para verificar a configuração do Django para deployment em subdiretório
Execute: python check_config.py
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
    
    print("\n" + "="*60)
    print("VERIFICAÇÃO DE CONFIGURAÇÃO DO DJANGO")
    print("="*60)
    
    # Verificar FORCE_SCRIPT_NAME
    print(f"\n✓ FORCE_SCRIPT_NAME: {settings.FORCE_SCRIPT_NAME or '(não configurado)'}")
    
    # Verificar STATIC_URL
    print(f"✓ STATIC_URL: {settings.STATIC_URL}")
    
    # Verificar SESSION_COOKIE_PATH
    print(f"✓ SESSION_COOKIE_PATH: {settings.SESSION_COOKIE_PATH}")
    
    # Verificar CSRF_COOKIE_PATH
    print(f"✓ CSRF_COOKIE_PATH: {settings.CSRF_COOKIE_PATH}")
    
    # Verificar CSRF_TRUSTED_ORIGINS
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        origins = settings.CSRF_TRUSTED_ORIGINS
        if origins:
            print(f"✓ CSRF_TRUSTED_ORIGINS: {', '.join(origins)}")
        else:
            print("⚠ CSRF_TRUSTED_ORIGINS: (não configurado - configure para produção!)")
    
    # Verificar ALLOWED_HOSTS
    if settings.DEBUG:
        print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS} (DEBUG=True)")
    else:
        print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            print("  ⚠ ATENÇÃO: Configure ALLOWED_HOSTS para produção!")
    
    # Verificar DEBUG
    print(f"\n✓ DEBUG: {settings.DEBUG}")
    if settings.DEBUG:
        print("  ⚠ ATENÇÃO: Desabilite DEBUG em produção!")
    
    # Testar geração de URLs
    print("\n" + "-"*60)
    print("TESTE DE GERAÇÃO DE URLs")
    print("-"*60)
    
    urls_to_test = [
        'home',
        'login',
        'cliente_list',
        'recorrencia_list',
    ]
    
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✓ {url_name:20s} -> {url}")
        except Exception as e:
            print(f"✗ {url_name:20s} -> ERRO: {e}")
    
    # Verificar configuração para subdiretório
    print("\n" + "-"*60)
    print("CONFIGURAÇÃO PARA SUBDIRETÓRIO")
    print("-"*60)
    
    if settings.FORCE_SCRIPT_NAME:
        print(f"\n✓ Configurado para rodar em subdiretório: {settings.FORCE_SCRIPT_NAME}")
        print(f"  URL esperada: http://SEU_IP{settings.FORCE_SCRIPT_NAME}/")
        
        # Verificar consistência
        issues = []
        
        if not settings.SESSION_COOKIE_PATH.startswith(settings.FORCE_SCRIPT_NAME):
            issues.append("SESSION_COOKIE_PATH não está configurado corretamente")
        
        if not settings.CSRF_COOKIE_PATH.startswith(settings.FORCE_SCRIPT_NAME):
            issues.append("CSRF_COOKIE_PATH não está configurado corretamente")
        
        if not settings.STATIC_URL.startswith(settings.FORCE_SCRIPT_NAME):
            issues.append("STATIC_URL não está configurado corretamente")
        
        if issues:
            print("\n⚠ PROBLEMAS ENCONTRADOS:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ Todas as configurações estão consistentes!")
    else:
        print("\n✓ Configurado para rodar na raiz (sem subdiretório)")
        print("  URL esperada: http://SEU_IP/")
    
    # Recomendações
    print("\n" + "="*60)
    print("RECOMENDAÇÕES PARA PRODUÇÃO")
    print("="*60)
    
    recommendations = []
    
    if settings.DEBUG:
        recommendations.append("Configure DEBUG=False no .env")
    
    if not hasattr(settings, 'CSRF_TRUSTED_ORIGINS') or not settings.CSRF_TRUSTED_ORIGINS:
        recommendations.append("Configure CSRF_TRUSTED_ORIGINS no .env")
        recommendations.append("Exemplo: CSRF_TRUSTED_ORIGINS=http://144.202.29.245")
    
    if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
        recommendations.append("Configure ALLOWED_HOSTS no .env")
        recommendations.append("Exemplo: ALLOWED_HOSTS=144.202.29.245,localhost")
    
    if settings.FORCE_SCRIPT_NAME and settings.FORCE_SCRIPT_NAME != '/gestor_asaas':
        recommendations.append(f"FORCE_SCRIPT_NAME está como '{settings.FORCE_SCRIPT_NAME}'")
        recommendations.append("Para o servidor VPS, deve ser: FORCE_SCRIPT_NAME=/gestor_asaas")
    
    if not settings.FORCE_SCRIPT_NAME:
        recommendations.append("Configure FORCE_SCRIPT_NAME=/gestor_asaas no .env do servidor VPS")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("\n✓ Configuração parece estar correta!")
    
    print("\n" + "="*60)
    print("Verificação concluída!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ ERRO ao verificar configuração: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
