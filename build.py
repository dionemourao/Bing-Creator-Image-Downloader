import os
import sys
import subprocess
import platform

def build_executable():
    # Determine the platform
    system = platform.system().lower()
    
    # Create the PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=BingImageDownloader',
        '--windowed',  # No console window
        '--onefile',   # Single executable
        '--add-data=config.toml:.',
        '--add-data=.env:.',
        '--add-data=images_clipboard.txt:.',
        '--icon=icon.ico' if system == 'windows' else '',
        '--hidden-import=PyQt6',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.sip',
        'gui.py'
    ]
    
    # Remove empty strings from command
    cmd = [x for x in cmd if x]
    
    # Run PyInstaller
    subprocess.run(cmd)

if __name__ == '__main__':
    build_executable() 