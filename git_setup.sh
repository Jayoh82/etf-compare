#!/bin/bash
cd "$(dirname "$0")"
echo "GitHub 저장소 연결 중..."
git remote add origin https://github.com/Jayoh82/etf-compare.git 2>/dev/null || git remote set-url origin https://github.com/Jayoh82/etf-compare.git
echo "push 중... (GitHub 로그인 창이 뜰 수 있습니다)"
git push -f origin main
echo ""
echo "완료!"
read -p "Enter 키를 누르면 닫힙니다..."
