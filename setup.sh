#!/bin/bash

echo "========================================"
echo "   Configurando Asaas Manager"
echo "========================================"
echo

echo "[1/5] Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar ambiente virtual"
    exit 1
fi

echo "[2/5] Ativando ambiente virtual..."
source venv/bin/activate

echo "[3/5] Instalando dependências..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi

echo "[4/5] Criando migrations..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar migrations"
    exit 1
fi

echo "[5/5] Aplicando migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao aplicar migrations"
    exit 1
fi

echo
echo "========================================"
echo "   Configuração concluída com sucesso!"
echo "========================================"
echo
echo "IMPORTANTE: Configure sua API KEY do Asaas no arquivo .env"
echo
echo "Para iniciar o servidor, execute:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo

