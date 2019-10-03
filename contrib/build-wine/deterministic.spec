# -*- mode: python3 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

import sys
for i, x in enumerate(sys.argv):
    if x == '--name':
        cmdline_name = sys.argv[i+1]
        break
else:
    raise BaseException('no name')

home = 'C:\\electroncash\\'

# see https://github.com/pyinstaller/pyinstaller/issues/2005
hiddenimports = []
hiddenimports += ['PyQt5.sip']
hiddenimports += collect_submodules('trezorlib')
hiddenimports += collect_submodules('btchip')
hiddenimports += collect_submodules('keepkeylib')
hiddenimports += collect_submodules('satochip') #Satochip
hiddenimports += collect_submodules('smartcard') #Satochip

# Add libusb binary
binaries = [("c:/tmp/libusb-1.0.dll", ".")]

# Add secp library
binaries += [('C:/tmp/libsecp256k1.dll', '.')]

# Add zbar libraries
binaries += [('C:/tmp/libzbar-0.dll', '.')]

# The below is no longer necessary. PyInstaller 3.4+ picks these up properly
# now and puts them in the Qt dirs.
# Add Windows OpenGL and D3D implementation DLLs (see #1255 and #1253)
#binaries += [
#    ('C:/python*/libEGL.dll', '.'),
#    ('C:/python*/libGLESv2.dll', '.'),
#    ('C:/python*/d3dcompiler_*.dll', '.'),
#    ('C:/python*/opengl32sw.dll', '.'),
#]

# Workaround for "Retro Look":
binaries += [b for b in collect_dynamic_libs('PyQt5') if 'qwindowsvista' in b[0]]

binaries += [('C:/python*/Lib/site-packages/smartcard/scard/_scard.cp36-win32.pyd', '.')] #satochip

datas = [
    (home+'lib/currencies.json', 'electroncash'),
    (home+'lib/servers.json', 'electroncash'),
    (home+'lib/servers_testnet.json', 'electroncash'),
    (home+'lib/wordlist/english.txt', 'electroncash/wordlist'),
    (home+'lib/locale', 'electroncash/locale'),
    (home+'gui/qt/data/ecsupplemental_win.ttf', 'electroncash_gui/qt/data'),
    (home+'plugins', 'electroncash_plugins'),
]
datas += collect_data_files('trezorlib')
datas += collect_data_files('btchip')
datas += collect_data_files('keepkeylib')
datas += collect_data_files('mnemonic')  # wordlists used by keepkeylib from lib mnemonic

# We don't put these files in to actually include them in the script but to make the Analysis method scan them for imports
a = Analysis([home+'electron-cash',
              home+'gui/qt/main_window.py',
              home+'gui/qt/qrreader/camera_dialog.py',
              home+'gui/text.py',
              home+'lib/util.py',
              home+'lib/wallet.py',
              home+'lib/simple_config.py',
              home+'lib/bitcoin.py',
              home+'lib/dnssec.py',
              home+'lib/commands.py',
              home+'plugins/cosigner_pool/qt.py',
              home+'plugins/email_requests/qt.py',
              home+'plugins/trezor/clientbase.py',
              home+'plugins/trezor/trezor.py',
              home+'plugins/trezor/qt.py',
              home+'plugins/keepkey/qt.py',
              home+'plugins/ledger/qt.py',
              home+'plugins/satochip/qt.py', #Satochip
              #home+'packages/requests/utils.py'
              ],
             binaries=binaries,
             datas=datas,
             #pathex=[home+'lib', home+'gui', home+'plugins'],
             hiddenimports=hiddenimports,
             hookspath=[])


rm_misc_datas = []
# http://stackoverflow.com/questions/19055089/pyinstaller-onefile-warning-pyconfig-h-when-importing-scipy-or-scipy-signal
rm_misc_datas.append('pyconfig.h')
print("Removing Misc. datas:", *rm_misc_datas)
for d in a.datas.copy():
    lcase_d0 = d[0].lower()
    if any(x in lcase_d0 for x in rm_misc_datas):
        a.datas.remove(d)
        print("----> Removed d =", d)

# Strip out parts of Qt that we never use. Reduces binary size by tens of MBs. see #4815
qt_bins2remove=('qt5web', 'qt53d', 'qt5game', 'qt5designer', 'qt5quick',
                'qt5location', 'qt5test', 'qt5xml', r'pyqt5\qt\qml\qtquick',
                'qt5qml', 'qt5printsupport', )
print("Removing Qt binaries:", *qt_bins2remove)
for x in a.binaries.copy():
    for r in qt_bins2remove:
        if x[0].lower().startswith(r):
            a.binaries.remove(x)
            print('----> Removed x =', x)
qt_data2remove=(r'pyqt5\qt\translations\qtwebengine_locales',
                r'pyqt5\qt\plugins\printsupport',
                r'pyqt5\qt\plugins\platforms\qwebgl',
                r'pyqt5\qt\plugins\platforms\qminimal', )
print("Removing Qt datas:", *qt_data2remove)
for x in a.datas.copy():
    for r in qt_data2remove:
        if r in x[1].lower():
            a.datas.remove(x)
            print('----> Removed x =', x)

# hotfix for #3171 (pre-Win10 binaries)
a.binaries = [x for x in a.binaries if not x[1].lower().startswith(r'c:\windows')]

pyz = PYZ(a.pure)


#####
# "standalone" exe with all dependencies packed into it

exe_standalone = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name=os.path.join('build\\pyi.win32\\electroncash', cmdline_name + ".exe"),
    debug=False,
    strip=None,
    upx=False,
    manifest=home+'contrib/build-wine/manifest.xml',
    icon=home+'icons/electron.ico',
    console=False)

exe_portable = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas + [ ('is_portable', 'README.md', 'DATA' ) ],
    name=os.path.join('build\\pyi.win32\\electroncash', cmdline_name + "-portable.exe"),
    debug=False,
    strip=None,
    upx=False,
    manifest=home+'contrib/build-wine/manifest.xml',
    icon=home+'icons/electron.ico',
    console=False)

#####
# exe and separate files that NSIS uses to build installer "setup" exe

exe_dependent = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=os.path.join('build\\pyi.win32\\electroncash', cmdline_name),
    debug=False,
    strip=None,
    upx=False,
    manifest=home+'contrib/build-wine/manifest.xml',
    icon=home+'icons/electron.ico',
    console=False)

coll = COLLECT(
    exe_dependent,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=None,
    upx=True,
    debug=False,
    icon=home+'icons/electron.ico',
    console=False,
    name=os.path.join('dist', 'electroncash'))
