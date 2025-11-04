#!/usr/bin/env python
"""
Script para criar o primeiro usuário do sistema de forma interativa
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def criar_usuario():
    print("=" * 60)
    print("CRIAR PRIMEIRO USUÁRIO - Asaas Manager")
    print("=" * 60)
    print()
    
    # Verificar se já existem usuários
    if User.objects.exists():
        print("⚠️  ATENÇÃO: Já existem usuários no sistema!")
        resposta = input("Deseja criar outro usuário mesmo assim? (s/N): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        print()
    
    # Solicitar dados
    print("Digite os dados do novo usuário:")
    print()
    
    # Username
    while True:
        username = input("Usuário: ").strip()
        if not username:
            print("❌ Usuário não pode ser vazio!")
            continue
        if User.objects.filter(username=username).exists():
            print(f"❌ Usuário '{username}' já existe!")
            continue
        break
    
    # Email
    email = input("E-mail (opcional): ").strip()
    
    # Senha
    while True:
        password1 = input("Senha: ")
        if not password1:
            print("❌ Senha não pode ser vazia!")
            continue
            
        password2 = input("Confirme a senha: ")
        
        if password1 != password2:
            print("❌ Senhas não conferem!")
            continue
        
        # Validar senha
        try:
            validate_password(password1)
            break
        except ValidationError as e:
            print(f"❌ Senha inválida:")
            for erro in e.messages:
                print(f"   - {erro}")
            print()
    
    # Criar usuário
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password1
        )
        
        print()
        print("=" * 60)
        print("✅ USUÁRIO CRIADO COM SUCESSO!")
        print("=" * 60)
        print()
        print(f"Usuário: {user.username}")
        if email:
            print(f"E-mail: {user.email}")
        print(f"Tipo: Superusuário (Admin)")
        print()
        print("🔐 Você já pode fazer login no sistema!")
        print()
        print("   URL de Login: http://localhost:8000/login/")
        print()
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERRO ao criar usuário: {str(e)}")
        print("=" * 60)

if __name__ == '__main__':
    try:
        criar_usuario()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nErro inesperado: {str(e)}")

