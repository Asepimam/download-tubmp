# -*- mode: python -*-
import os

block_cipher = None

# Path ke folder ffmpeg relatif terhadap direktori kerja saat ini
ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg')
ffmpeg_binaries = []

# Menambahkan semua file dalam folder ffmpeg sebagai binaries
if os.path.exists(ffmpeg_path):
    for root, dirs, files in os.walk(ffmpeg_path):
        for file in files:
            ffmpeg_binaries.append(
                (os.path.join(root, file), os.path.relpath(root, os.getcwd()))
            )

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=ffmpeg_binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'termios',
        'grp',
        'pwd',
        'fcntl',
        'posix',
        'resource',
        '_posixsubprocess'
    ],
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
    name='yt2mp3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
