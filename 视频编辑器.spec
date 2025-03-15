
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('video_editor_app', 'video_editor_app')],
    hiddenimports=['cv2', 'moviepy', 'moviepy.editor', 'numpy', 'PyQt5', 'PyQt5.QtCore', 
                  'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 添加PyQt5多媒体库
try:
    from PyQt5.QtMultimedia import QMediaPlayer
    print("成功导入QMediaPlayer")
except ImportError:
    print("警告: 无法导入QMediaPlayer")

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='视频编辑器',
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
    icon='resources/icon.icns',
)

app = BUNDLE(
    exe,
    name='视频编辑器.app',
    icon='resources/icon.icns',
    bundle_identifier='com.videoeditor.app',
)
