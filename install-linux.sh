#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Bing Image Downloader installation...${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please don't run this script as root${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Please install it first.${NC}"
    exit 1
fi

# Install required packages
echo -e "${GREEN}Installing required packages...${NC}"
pip3 install -r requirements.txt

# Build the application
echo -e "${GREEN}Building the application...${NC}"
python3 build.py

# Create necessary directories
echo -e "${GREEN}Creating installation directories...${NC}"
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons

# Copy the executable
echo -e "${GREEN}Installing the application...${NC}"
cp dist/BingImageDownloader ~/.local/bin/bing-image-downloader
chmod +x ~/.local/bin/bing-image-downloader

# Convert icon to PNG if not exists
if [ ! -f icon.png ]; then
    echo -e "${GREEN}Converting icon to PNG format...${NC}"
    if command -v convert &> /dev/null; then
        convert icon.ico icon.png
    else
        echo -e "${RED}ImageMagick not found. Please install it to convert the icon.${NC}"
        exit 1
    fi
fi

# Copy the icon
echo -e "${GREEN}Installing icon...${NC}"
cp icon.png ~/.local/share/icons/bing-image-downloader.png

# Create desktop file
echo -e "${GREEN}Creating desktop shortcut...${NC}"
cat > ~/.local/share/applications/bing-image-downloader.desktop << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=Bing Image Downloader
Comment=Download images from Bing Image Creator
Exec=bing-image-downloader
Icon=bing-image-downloader
Terminal=false
Categories=Graphics;Utility;
EOL

# Update desktop database
echo -e "${GREEN}Updating desktop database...${NC}"
update-desktop-database ~/.local/share/applications

# Clear GNOME application cache
echo -e "${GREEN}Clearing GNOME application cache...${NC}"
rm -f ~/.cache/gnome-applications.menu
rm -f ~/.cache/gnome-applications.menu.cache
rm -f ~/.cache/gnome-applications.menu.cache-*

echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "You can now find Bing Image Downloader in your applications menu."
echo -e "To run it from terminal, use: bing-image-downloader"
echo -e "You may need to log out and log in again to see the changes in the applications menu." 