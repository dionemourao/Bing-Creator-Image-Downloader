# Bing-Creator-Image-Downloader
Downloads all Bing Creator images from a collection

### Prerequisites
* [Python 3.11+](https://www.python.org/downloads/)

### How to use
#### GUI Application
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the GUI application:
   ```bash
   python gui.py
   ```
3. Configure the download settings:
   - Choose between API or File download method
   - For API method, enter your _U cookie value
   - Specify collections to download (comma-separated)
   - Configure filename pattern and other options
4. Click "Start Download" to begin

#### Building Executables

### Windows
1. Install Python 3.13 from [python.org](https://www.python.org/downloads/)
2. Clone the repository:
   ```bash
   git clone https://github.com/seu-usuario/Bing-Creator-Image-Downloader.git
   cd Bing-Creator-Image-Downloader
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Build the executable:
   ```bash
   python -m PyInstaller --name=BingImageDownloader --windowed --onedir --add-data "config.toml;." --add-data ".env;." --add-data "images_clipboard.txt;." gui.py
   ```
5. The executable will be in the `dist/BingImageDownloader` folder

### Linux (Ubuntu/Debian)
1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv python3-pyqt6
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/seu-usuario/Bing-Creator-Image-Downloader.git
   cd Bing-Creator-Image-Downloader
   ```
3. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Build the executable:
   ```bash
   python3 -m PyInstaller --name=BingImageDownloader --windowed --onedir --add-data "config.toml:." --add-data ".env:." --add-data "images_clipboard.txt:." gui.py
   ```
6. The executable will be in the `dist/BingImageDownloader` folder

### Linux (Fedora)
1. Install system dependencies:
   ```bash
   sudo dnf install python3 python3-pip python3-venv python3-qt6
   ```
2. Follow steps 2-6 from Ubuntu instructions

### Linux (Arch Linux)
1. Install system dependencies:
   ```bash
   sudo pacman -S python python-pip python-venv python-pyqt6
   ```
2. Follow steps 2-6 from Ubuntu instructions

### macOS
1. Install Python 3.13 (using Homebrew recommended):
   ```bash
   brew install python@3.13
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/seu-usuario/Bing-Creator-Image-Downloader.git
   cd Bing-Creator-Image-Downloader
   ```
3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Build the executable:
   ```bash
   python3 -m PyInstaller --name=BingImageDownloader --windowed --onedir --add-data "config.toml:." --add-data ".env:." --add-data "images_clipboard.txt:." --icon="icon.ico" gui.py
   ```
5. The application will be in the `dist` folder as `BingImageDownloader.app`

Note: The executables are platform-specific. You need to build them on each target operating system.

#### Command Line Usage
* Clone the repository or download and unzip
#### Collection API method:
* Get your `_U` cookie for Bing. For example like described in this [comment](https://old.reddit.com/r/bing/comments/172rpo6/is_there_any_way_to_download_image_collections/k72vjqs/) or this [package](https://pypi.org/project/sydney-py/)
* Paste the value after the equals sign for the `_U` property in the `COOKIE` property in the `.env.example` file.
* Add your own collections to the `collections_to_include` property in the `config.toml` or leave the array empty to download for all collections
* Rename the `.env.example` file to `.env`
#### Clipboard file method:
* Go to the collection you want to download at https://www.bing.com/saves
* Scroll down until all images are loaded
* Click the `Select all results in this collection button`
* Click the `Copy items to clipboard button`
* Wait until all images are copied to the clipboard (it may take a while)
* Paste the clipboard content into the `images_clipboard.txt.example` file
* Remove the `.example` from the file name so it's called `images_clipboard.txt`
#### Shared next steps:
* Check in the `config.toml` if the correct image source method is selected
* Navigate to the folder of the repository
* Open a terminal e.g. PowerShell
* Run `pip install -r .\requirements.txt` to install all dependencies (You may need to add the `PythonXX\Scripts` folder to your PATH first)
* Run `python .\main.py` afterward to run the script 
* The images of the collection are saved in the `bing_images_$TodaysDate.zip` file

### Addendum
Each image contains the original prompt, used image link and creation date as EXIF Metadata in the `UserComment` field in a JSON format.  
It is also saved in the XPComment field, so you can view and edit it directly in the Windows Explorer.  
If you encounter any errors or have some requests, please open a new issue or discussion.
