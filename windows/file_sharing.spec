# -*- mode: python ; coding: utf-8 -*-

import platform
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all pyngrok packages and data
pyngrok_datas, pyngrok_binaries, pyngrok_hiddenimports = collect_all('pyngrok')

a = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=pyngrok_binaries,
    datas=pyngrok_datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'pyngrok',
        'pyngrok.conf',
        'pyngrok.ngrok',
        'qrcode',
        'Pillow',
    ] + pyngrok_hiddenimports,
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

if platform.system() == 'Darwin':  # macOS
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='FileSharing',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # GUI only
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,
        bundle_identifier='com.filesharing.app',
    )
    
    app = BUNDLE(
        exe,
        name='FileSharing.app',
        icon=None,
        bundle_identifier='com.filesharing.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleName': 'FileSharing',
        },
    )

else:  # Windows
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='FileSharing',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # GUI only
        disable_windowed_traceback=False,
        target_arch=None,
    )