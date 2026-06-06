#!/bin/bash
cd "$(dirname "$0")"
echo "기존 .git 폴더 제거 중..."
rm -rf .git
echo "git 초기화 중..."
git init
git config user.email "gjayoh@gmail.com"
git config user.name "jaehwan"
git branch -m main
git add .
git commit -m "ETF init"
echo ""
echo "완료! 결과를 확인하세요."
read -p "Enter 키를 누르면 닫힙니다..."
