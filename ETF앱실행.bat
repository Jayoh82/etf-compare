@echo off
start "" "http://localhost:8501"
python -m streamlit run "%~dp0etf_app.py" --server.headless true
