@echo off
echo Building Radar Promo .exe...
cd /d D:\Ujicoba
python -m PyInstaller radar_promo.spec --clean --noconfirm --add-data "admin_tool.py;."
echo Done! Check dist\RadarPromo folder
pause