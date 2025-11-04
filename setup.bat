@echo off
echo ========================================
echo   Configurando Asaas Manager
echo ========================================
echo.

echo [1/5] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual
    pause
    exit /b 1
)

echo [2/5] Ativando ambiente virtual...
call venv\Scripts\activate

echo [3/5] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [4/5] Criando migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo ERRO: Falha ao criar migrations
    pause
    exit /b 1
)

echo [5/5] Aplicando migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERRO: Falha ao aplicar migrations
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Configuracao concluida com sucesso!
echo ========================================
echo.
echo IMPORTANTE: Configure sua API KEY do Asaas no arquivo .env
echo.
echo Para iniciar o servidor, execute:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
pause

