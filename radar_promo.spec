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
        ('map.html', '.'),
        ('assets', 'assets'),
        ('Font', 'Font'),
        ('data_promo.json', '.'),
        ('rekomendasi.json', '.'),
        ('activity.log', '.'),
        ('admin_tool.py', '.'),
    ],
    hiddenimports=[
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebChannel',
        'data_manager', 'engine', 'gui_pyqt', 'scraper', 'admin_tool',
        'radar_promo', 'claude',
        'requests', 'urllib.request', 'urllib.error', 'logging', 'json', 'PIL',
        'matplotlib', 'matplotlib.pyplot', 'matplotlib.figure',
        'folium', 'folium.folium',
        'bs4', 'beautifulsoup4',
        'math', 'datetime', 'threading', 'copy',
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)