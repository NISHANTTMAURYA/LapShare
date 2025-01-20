# -*- mode: python ; coding: utf-8 -*-

import platform
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all pyngrok and yaml packages and data
pyngrok_datas, pyngrok_binaries, pyngrok_hiddenimports = collect_all('pyngrok')
yaml_datas, yaml_binaries, yaml_hiddenimports = collect_all('yaml')

a = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=pyngrok_binaries + yaml_binaries,
    datas=[
        ('http_server.py', '.'),
        ('.env', '.'),
    ] + pyngrok_datas + yaml_datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'pyngrok',
        'pyngrok.conf',
        'pyngrok.ngrok',
        'qrcode',
        'Pillow',
        'python-dotenv',
        'dotenv',
        'yaml',
        'yaml.loader',
        'yaml.dumper',
        'yaml.parser',
        'yaml.emitter',
        'yaml.serializer',
        'yaml.representer',
        'yaml.resolver',
        'yaml.constructor'
    ] + pyngrok_hiddenimports + yaml_hiddenimports,
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