# -*- mode: python -*-
# This file is released under public domain
# Code 'extra_datas' is copied from StackOverflow:Q11322538.

block_cipher = None

a = Analysis(['ezhuthi.py'],
             pathex=['c:\\Users\\muthu\\devel\\ezhil-editor'],
             binaries=[],
             datas=[('res/editor.glade', 'res'), ('res/helper.glade', 'res'), ('res/img/ezhil_square_2015_128px.png', 'res/img'), ('res/img/small-ezhil-splash-5.png', 'res/img')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas
###########################################

# append the 'data' dir
a.datas += extra_datas('examples')
a.datas += extra_datas('xmlbook')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ezhuthi',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='ezhil16.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ezhuthi')
