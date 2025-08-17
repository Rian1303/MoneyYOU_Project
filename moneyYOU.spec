# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# =========================
# Incluir arquivos extras
# =========================
datas = []

# Inclui toda a pasta 'assets' com estrutura preservada
for root, dirs, files in os.walk('assets'):
    for file in files:
        src_path = os.path.join(root, file)
        dest_path = os.path.relpath(root, '.')  # mantém estrutura
        datas.append((src_path, dest_path))

# Inclui a chave do Firebase
datas.append(('config/firebase_key.json', 'config'))

# =========================
# Configuração PyInstaller
# =========================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'firebase_admin',
        'google.auth',
        'google.auth.transport.requests',
        'requests'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# =========================
# EXE Final
# =========================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,   # importante para onefile
    name='MoneyYOU',
    debug=False,
    strip=False,
    upx=True,
    console=True,  # coloque False se quiser app sem terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icons/app_icon.ico'],  # ajuste seu ícone
)

# =========================
# Coletando tudo (onedir)
# =========================
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MoneyYOU',
)
