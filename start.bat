@echo off
chcp 65001 > nul
title 自動抽卡腳本
echo 正在啟動腳本...
python template_matching.py
pause 