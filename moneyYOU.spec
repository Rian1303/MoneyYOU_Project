# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# =========================
# Base do projeto
# =========================
BASE_DIR = os.getcwd()

# =========================
# Incluir arquivos extras
# =========================
datas = []

# Firebase key
firebase_key_path = os.path.join(BASE_DIR, 'config', 'firebase_key.json')
datas.append((firebase_key_path, 'config'))

# Banco local
data_json_path = os.path.join(BASE_DIR, 'database', 'data.json')
datas.append((data_json_path, 'database'))

# Assets
for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'assets')):
    for file in files:
        src_path = os.path.join(root, file)
        dest_path = os.path.relpath(root, BASE_DIR)
        datas.append((src_path, dest_path))

# =========================
# Configuração PyInstaller
# =========================
a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
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
# EXE Final (onedir)
# =========================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='MoneyYOU',
    debug=False,
    strip=False,
    upx=True,
    console=True,  # colocar False se não quiser console
    disable_windowed_traceback=False,
    icon=os.path.join(BASE_DIR, 'assets', 'icons', 'app_icon.ico')
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

hiddenimports=[
    'firebase_admin',
    'firebase_admin.credentials',
    'firebase_admin.firestore',
    'google.auth',
    'google.auth.transport.requests',
    'google.auth.compute_engine',
    'google.auth.jwt',
    'google.oauth2.service_account',
    'requests',
]