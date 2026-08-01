# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        (r'C:\Users\Arya\AppData\Roaming\Python\Python314\site-packages\PyQt6\Qt6\bin\QtWebEngineProcess.exe', '.'),
    ],
    datas=[
        ('assets', 'assets'),
        ('UI', 'UI'),
        ('Font', 'Font'),
        ('data_promo.json', '.'),
        ('rekomendasi.json', '.'),
        ('gemini-svg.png', '.'),
        ('gemini-svg.ico', '.'),
    ],
    hiddenimports=[
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebChannel',
        'qtawesome', 'data_manager', 'engine', 'gui_pyqt', 'scraper',
        'admin_tool', 'requests', 'PIL', 'PIL.Image', 'matplotlib',
        'matplotlib.pyplot', 'matplotlib.figure', 'bs4', 'beautifulsoup4',
        'folium', 'math', 'datetime', 'threading', 'copy', 'logging', 'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RadarPromo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gemini-svg.ico',
    onefile=True,
)
