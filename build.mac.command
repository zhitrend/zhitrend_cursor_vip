#!/bin/bash
cd "$(dirname "$0")"

echo "正在創建虛擬環境..."
python3 -m venv venv

echo "啟動虛擬環境..."
source venv/bin/activate

echo "安裝依賴..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "開始構建..."
python build.py

echo "清理虛擬環境..."
deactivate
rm -rf venv

echo "完成！"
read -p "按任意鍵退出..." 