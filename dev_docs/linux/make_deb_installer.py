# Run this script after doing the pyinstaller build

import os
import shutil
import subprocess

version = '0.9.8'

os.sys.path.append(os.path.abspath(os.path.join('..', '..')))

deb_path = os.path.join('.', 'chiplot-analyze-{}_amd64(linux)'.format(version),
    'DEBIAN')
exc_path = os.path.join('.', 'chiplot-analyze-{}_amd64(linux)'.format(version),
    'usr', 'bin')
app_path = os.path.join('.', 'chiplot-analyze-{}_amd64(linux)'.format(version),
    'usr', 'share', 'applications')
png_path = os.path.join('.', 'chiplot-analyze-{}_amd64(linux)'.format(version),
    'usr', 'share', 'icons')

os.makedirs(deb_path, exist_ok=True)
os.makedirs(exc_path, exist_ok=True)
os.makedirs(app_path, exist_ok=True)
os.makedirs(png_path, exist_ok=True)

shutil.copy('control', deb_path)
shutil.copy(os.path.join('..', '..', 'dist', 'chiplot-analyze'), exc_path)
shutil.copy('chiplot.desktop', app_path)
shutil.copy('AppIcon.icns', os.path.join(png_path, 'AppIcon.icns'))

with open(os.path.join(deb_path, 'control'), 'r') as f:
    control_lines = f.readlines()

for i in range(len(control_lines)):
    if control_lines[i].startswith('Version'):
        control_lines[i] = 'Version: {}\n'.format(version)

with open(os.path.join(deb_path, 'control'), 'w') as f:
    f.writelines(control_lines)

proc = subprocess.Popen("fakeroot dpkg-deb --build chiplot-analyze-{}_amd64\(linux\)".format(version),
    shell=True)
proc.communicate()

print('Checking .deb installer with lintian')
proc = subprocess.Popen("lintian chiplot-analyze-{}_amd64\(linux\).deb".format(version), shell=True)
proc.communicate()
