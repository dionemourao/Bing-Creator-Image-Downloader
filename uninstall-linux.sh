#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Removing Bing Image Downloader...${NC}"

# Remove executable
echo -e "${GREEN}Removing executable...${NC}"
rm -f ~/.local/bin/BingImageDownloader
rm -f ~/.local/bin/bing-image-downloader

# Remove icon
echo -e "${GREEN}Removing icon...${NC}"
rm -f ~/.local/share/icons/bing-image-downloader.png
rm -f ~/.local/share/icons/BingImageDownloader.png

# Remove desktop files
echo -e "${GREEN}Removing desktop shortcuts...${NC}"
rm -f ~/.local/share/applications/bing-image-downloader.desktop
rm -f ~/.local/share/applications/BingImageDownloader.desktop

# Remove any remaining files in applications directory
find ~/.local/share/applications -name "*bing*" -o -name "*Bing*" -delete

# Update desktop database and clear caches
echo -e "${GREEN}Updating desktop database and clearing caches...${NC}"
update-desktop-database ~/.local/share/applications
gtk-update-icon-cache -f -t ~/.local/share/icons

# Clear GNOME application cache
echo -e "${GREEN}Clearing GNOME application cache...${NC}"
rm -f ~/.cache/gnome-applications.menu
rm -f ~/.cache/gnome-applications.menu.cache
rm -f ~/.cache/gnome-applications.menu.cache-*

echo -e "${GREEN}Uninstallation completed successfully!${NC}"
echo -e "You may need to log out and log in again to see the changes in the applications menu." 