@echo off
echo Iniciando Buscador de Jurisprudencia de la SCJN...
echo Por favor, espere un momento...
call venv\Scripts\activate.bat
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
streamlit run app_buscador.py --browser.gatherUsageStats false
pause
