@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo --- git status ---
git status
echo.
echo --- git init (if needed) ---
git init
git config user.email "gjayoh@gmail.com"
git config user.name "jaehwan"
git branch -M main
git add .
git commit -m "update" --allow-empty
echo.
echo --- remote setup ---
git remote remove origin 2>nul
git remote add origin https://github.com/Jayoh82/etf-compare.git
echo.
echo --- push ---
git push -f origin main
echo.
echo DONE.
pause
