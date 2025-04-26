import os
import sys
import asyncio
import platform
import subprocess
import json
import locale
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QCheckBox, QFileDialog, QMessageBox,
                            QGroupBox, QTextEdit, QProgressBar, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from dotenv import load_dotenv
from models.image_download import ImageDownload
from utilities.config import Config

# Configuration file path
CONFIG_FILE = Path.home() / '.bing_image_downloader_config.json'

# Translations
TRANSLATIONS = {
    'en_US': {
        'window_title': "Bing Image Downloader",
        'config_group': "Configuration",
        'image_source': "Image Source:",
        'cookie_label': "Cookie:",
        'cookie_help': "To get your _U cookie:\n1. Open Bing Image Creator in your browser\n2. Press F12 to open Developer Tools\n3. Go to Application/Storage tab\n4. Find and copy the _U cookie value",
        'collections_label': "Collections:",
        'destination_folder': "Destination Folder:",
        'filename_pattern': "Filename Pattern:",
        'use_local_time': "Use Local Time Zone",
        'delete_collection': "Delete Collection After Download",
        'detailed_stats': "Generate Detailed Statistics",
        'progress_group': "Progress",
        'start_download': "Start Download",
        'cancel': "Cancel",
        'select_folder': "Select Download Folder",
        'error_no_cookie': "Please enter your cookie for API method",
        'error_no_collections': "Please enter at least one collection name",
        'error_no_folder': "Please select a destination folder",
        'error_create_folder': "Could not create destination folder: {}",
        'starting_download': "Starting download...",
        'download_completed': "Download completed!",
        'successful_downloads': "Successfully downloaded {} of {} images",
        'time_elapsed': "Time elapsed: {:.2f} seconds",
        'download_cancelled': "Download cancelled",
        'system_limits': "System Limits (macOS)",
        'max_connections': "Max Connections:",
        'memory_limit': "Memory Limit (MB):"
    },
    'pt_BR': {
        'window_title': "Bing Image Downloader",
        'config_group': "Configuração",
        'image_source': "Fonte da Imagem:",
        'cookie_label': "Cookie:",
        'cookie_help': "Para obter seu cookie _U:\n1. Abra o Bing Image Creator no seu navegador\n2. Pressione F12 para abrir as Ferramentas do Desenvolvedor\n3. Vá para a aba Application/Storage\n4. Encontre e copie o valor do cookie _U",
        'collections_label': "Coleções:",
        'destination_folder': "Pasta de Destino:",
        'filename_pattern': "Padrão do Nome do Arquivo:",
        'use_local_time': "Usar Fuso Horário Local",
        'delete_collection': "Excluir Coleção Após Download",
        'detailed_stats': "Gerar Estatísticas Detalhadas",
        'progress_group': "Progresso",
        'start_download': "Iniciar Download",
        'cancel': "Cancelar",
        'select_folder': "Selecionar Pasta de Download",
        'error_no_cookie': "Por favor, insira seu cookie para o método API",
        'error_no_collections': "Por favor, insira pelo menos um nome de coleção",
        'error_no_folder': "Por favor, selecione uma pasta de destino",
        'error_create_folder': "Não foi possível criar a pasta de destino: {}",
        'starting_download': "Iniciando download...",
        'download_completed': "Download concluído!",
        'successful_downloads': "Download bem-sucedido de {} de {} imagens",
        'time_elapsed': "Tempo decorrido: {:.2f} segundos",
        'download_cancelled': "Download cancelado",
        'system_limits': "Limites do Sistema (macOS)",
        'max_connections': "Conexões Máximas:",
        'memory_limit': "Limite de Memória (MB):"
    }
}

# Get system language
def get_system_language():
    try:
        lang = locale.getdefaultlocale()[0]
        return lang if lang in TRANSLATIONS else 'en_US'
    except:
        return 'en_US'

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, int, float)
    error = pyqtSignal(str)

    def __init__(self, config, connection_limit=None, memory_limit=None, destination_folder=None):
        super().__init__()
        self.config = config
        self.image_download = ImageDownload()
        self.start_time = None
        self.connection_limit = connection_limit
        self.memory_limit = memory_limit
        self.destination_folder = destination_folder

    def run(self):
        try:
            # Set system limits if on macOS
            if platform.system() == 'Darwin':
                try:
                    # Try to set limits with admin privileges
                    if self.connection_limit:
                        result = subprocess.run(['ulimit', '-n', str(self.connection_limit)], 
                                             capture_output=True, text=True)
                        if result.returncode != 0:
                            # If failed, use default safe values
                            self.connection_limit = 1024  # Default safe value
                            result = subprocess.run(['ulimit', '-n', '1024'], 
                                                 capture_output=True, text=True)
                    
                    if self.memory_limit:
                        result = subprocess.run(['ulimit', '-v', str(self.memory_limit)], 
                                             capture_output=True, text=True)
                        if result.returncode != 0:
                            # If failed, use default safe value
                            self.memory_limit = 512 * 1024  # 512 MB in KB
                            result = subprocess.run(['ulimit', '-v', '524288'], 
                                                 capture_output=True, text=True)
                except Exception as e:
                    # If any error occurs, use default values and continue
                    self.connection_limit = 1024
                    self.memory_limit = 512 * 1024
                    print(f"Using default system limits due to: {str(e)}")

            # Set the config before running
            Config._config = self.config

            # Set destination folder if specified
            if self.destination_folder:
                # Change current working directory to destination folder
                os.chdir(self.destination_folder)
                # Set environment variable for the download process
                os.environ['DESTINATION_FOLDER'] = str(self.destination_folder)

            # Create and set new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.start_time = loop.time()
            loop.run_until_complete(self.image_download.run())
            end_time = loop.time()
            elapsed_time = end_time - self.start_time
            
            self.finished.emit(
                self.image_download.successful_image_count,
                self.image_download.total_image_count,
                elapsed_time
            )
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # Clean up the event loop
            if 'loop' in locals():
                loop.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = get_system_language()
        self.translations = TRANSLATIONS[self.language]
        
        self.setWindowTitle(self.translations['window_title'])
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create configuration group
        config_group = QGroupBox(self.translations['config_group'])
        config_layout = QVBoxLayout()

        # Image Source Method
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel(self.translations['image_source']))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["API", "File"])
        source_layout.addWidget(self.source_combo)
        config_layout.addLayout(source_layout)

        # Cookie Input (for API method)
        cookie_layout = QVBoxLayout()
        cookie_label_layout = QHBoxLayout()
        cookie_label_layout.addWidget(QLabel(self.translations['cookie_label']))
        cookie_label_layout.addWidget(self.source_combo)
        cookie_layout.addLayout(cookie_label_layout)
        
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("Enter your _U cookie value")
        cookie_layout.addWidget(self.cookie_input)
        
        # Add cookie help label
        cookie_help = QLabel(self.translations['cookie_help'])
        cookie_help.setWordWrap(True)
        cookie_help.setStyleSheet("color: gray; font-size: 10pt;")
        cookie_layout.addWidget(cookie_help)
        
        config_layout.addLayout(cookie_layout)

        # Collections to Include
        collections_layout = QHBoxLayout()
        collections_layout.addWidget(QLabel(self.translations['collections_label']))
        self.collections_input = QLineEdit()
        self.collections_input.setPlaceholderText("Comma-separated collection names")
        collections_layout.addWidget(self.collections_input)
        config_layout.addLayout(collections_layout)

        # Destination Folder
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel(self.translations['destination_folder']))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select download folder")
        folder_layout.addWidget(self.folder_input)
        self.browse_button = QPushButton(self.translations['select_folder'])
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        config_layout.addLayout(folder_layout)

        # Filename Pattern
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel(self.translations['filename_pattern']))
        self.pattern_input = QLineEdit()
        self.pattern_input.setText("$date$sep$index$sep$prompt")
        pattern_layout.addWidget(self.pattern_input)
        config_layout.addLayout(pattern_layout)

        # System Limits (macOS only)
        if platform.system() == 'Darwin':
            limits_group = QGroupBox(self.translations['system_limits'])
            limits_layout = QVBoxLayout()

            # Connection Limit
            connection_layout = QHBoxLayout()
            connection_layout.addWidget(QLabel(self.translations['max_connections']))
            self.connection_limit = QSpinBox()
            self.connection_limit.setRange(256, 65536)
            self.connection_limit.setValue(1024)
            self.connection_limit.setSingleStep(256)
            connection_layout.addWidget(self.connection_limit)
            limits_layout.addLayout(connection_layout)

            # Memory Limit
            memory_layout = QHBoxLayout()
            memory_layout.addWidget(QLabel(self.translations['memory_limit']))
            self.memory_limit = QSpinBox()
            self.memory_limit.setRange(256, 16384)
            self.memory_limit.setValue(1024)
            self.memory_limit.setSingleStep(256)
            memory_layout.addWidget(self.memory_limit)
            limits_layout.addLayout(memory_layout)

            limits_group.setLayout(limits_layout)
            config_layout.addWidget(limits_group)

        # Options
        options_layout = QVBoxLayout()
        self.use_local_time = QCheckBox(self.translations['use_local_time'])
        self.use_local_time.setChecked(True)
        self.delete_collection = QCheckBox(self.translations['delete_collection'])
        self.detailed_stats = QCheckBox(self.translations['detailed_stats'])
        options_layout.addWidget(self.use_local_time)
        options_layout.addWidget(self.delete_collection)
        options_layout.addWidget(self.detailed_stats)
        config_layout.addLayout(options_layout)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Progress Group
        progress_group = QGroupBox(self.translations['progress_group'])
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        progress_layout.addWidget(self.log_output)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton(self.translations['start_download'])
        self.start_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton(self.translations['cancel'])
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        # Initialize download thread
        self.download_thread = None

        # Load saved configuration
        self.load_config()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.translations['select_folder'])
        if folder:
            self.folder_input.setText(folder)

    def load_config(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                # Restore values
                self.source_combo.setCurrentText(config.get('source', 'API'))
                self.cookie_input.setText(config.get('cookie', ''))
                self.collections_input.setText(config.get('collections', ''))
                self.folder_input.setText(config.get('destination_folder', ''))
                self.pattern_input.setText(config.get('pattern', '$date$sep$index$sep$prompt'))
                self.use_local_time.setChecked(config.get('use_local_time', True))
                self.delete_collection.setChecked(config.get('delete_collection', False))
                self.detailed_stats.setChecked(config.get('detailed_stats', False))
                
                if platform.system() == 'Darwin':
                    self.connection_limit.setValue(config.get('connection_limit', 1024))
                    self.memory_limit.setValue(config.get('memory_limit', 1024))
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")

    def save_config(self):
        try:
            config = {
                'source': self.source_combo.currentText(),
                'cookie': self.cookie_input.text(),
                'collections': self.collections_input.text(),
                'destination_folder': self.folder_input.text(),
                'pattern': self.pattern_input.text(),
                'use_local_time': self.use_local_time.isChecked(),
                'delete_collection': self.delete_collection.isChecked(),
                'detailed_stats': self.detailed_stats.isChecked()
            }
            
            if platform.system() == 'Darwin':
                config.update({
                    'connection_limit': self.connection_limit.value(),
                    'memory_limit': self.memory_limit.value()
                })
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")

    def start_download(self):
        # Validate inputs
        if self.source_combo.currentText() == "API" and not self.cookie_input.text():
            QMessageBox.warning(self, "Error", self.translations['error_no_cookie'])
            return

        # Validate collections
        collections = [c.strip() for c in self.collections_input.text().split(',') if c.strip()]
        if not collections:
            QMessageBox.warning(self, "Error", self.translations['error_no_collections'])
            return

        # Validate destination folder
        destination_folder = self.folder_input.text().strip()
        if not destination_folder:
            QMessageBox.warning(self, "Error", self.translations['error_no_folder'])
            return
        if not os.path.exists(destination_folder):
            try:
                os.makedirs(destination_folder)
            except Exception as e:
                QMessageBox.warning(self, "Error", self.translations['error_create_folder'].format(str(e)))
                return

        # Save configuration
        self.save_config()

        # Update config
        config = {
            'filename': {
                'filename_pattern': self.pattern_input.text(),
                'use_local_time_zone': self.use_local_time.isChecked()
            },
            'collection': {
                'collections_to_include': collections,
                'delete_collection_after_download': {
                    'toggle': self.delete_collection.isChecked(),
                    'mode': 'safest'
                }
            },
            'image_source': {
                'method': 'api' if self.source_combo.currentText() == "API" else 'file'
            },
            'debug': {
                'debug': True,
                'use_log_file': True,
                'debug_filename': "bing_image_creator.log",
                'detailed_statistics': self.detailed_stats.isChecked()
            },
            'detail_api': {
                'max_attempts': 5
            }
        }

        # Update environment
        if self.source_combo.currentText() == "API":
            cookie = self.cookie_input.text().strip()
            if not cookie.startswith('_U='):
                cookie = f'_U={cookie}'
            os.environ['COOKIE'] = cookie
            self.log_output.append(f"Using cookie: {cookie[:20]}...")

        # Log configuration
        self.log_output.append(f"Starting download with configuration:")
        self.log_output.append(f"Method: {config['image_source']['method']}")
        self.log_output.append(f"Collections: {', '.join(collections)}")
        self.log_output.append(f"Destination folder: {destination_folder}")
        self.log_output.append(f"Filename pattern: {config['filename']['filename_pattern']}")

        # Get system limits if on macOS
        connection_limit = None
        memory_limit = None
        if platform.system() == 'Darwin':
            connection_limit = self.connection_limit.value()
            memory_limit = self.memory_limit.value() * 1024  # Convert MB to KB
            self.log_output.append(f"System limits:")
            self.log_output.append(f"Max connections: {connection_limit}")
            self.log_output.append(f"Memory limit: {self.memory_limit.value()} MB")

        # Start download
        self.download_thread = DownloadThread(config, connection_limit, memory_limit, destination_folder)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.start()

        # Update UI
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.log_output.append(self.translations['starting_download'])

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
            self.log_output.append(self.translations['download_cancelled'])
            self.start_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def download_finished(self, successful, total, elapsed):
        self.log_output.append(f"\n{self.translations['download_completed']}\n"
                             f"{self.translations['successful_downloads'].format(successful, total)}\n"
                             f"{self.translations['time_elapsed'].format(elapsed)}")
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def download_error(self, error_msg):
        self.log_output.append(f"\nError: {error_msg}")
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def closeEvent(self, event):
        # Save configuration when closing the application
        self.save_config()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 