# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(['xeno.py'],
             pathex=['/Users/tsukasayamatomi/Public/myapp/sample/xeno'],
             binaries=[],
             datas=[('xeno.kv', '.'), ('*.png', '.'), ('ipaexg.ttf', '.')],
             hiddenimports=['win32file', 'win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['numpy', 'pandas'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='xeno',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='icon.co')
app = BUNDLE(exe,
             name='xeno.app',
             icon='icon.co',
             bundle_identifier=None)
