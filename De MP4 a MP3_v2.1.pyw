
#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Desarrollado Por: Cristian M. Veliz Cano
Adaptado a PyQt5 - Versión Estable con Cancelación entre Archivos

🎯 Soft - EN MEGA:
✨ DE MP4 a MP3 ✨ (Versión Estable con Cancelación entre Archivos)
➜ https://mega.nz/file/vwkkGBxK#Vu-f-29orqpK6F775P9xyu-md3sGMjXCnCRpmESxZgQ
'''
##====================================================================================
import sys
import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, 
    QMessageBox, QDialog, QProgressBar, QLabel, QPushButton as QBtn)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QIcon

import moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip

##====================================================================================
# --- Clase para manejo de rutas de recursos ---
##====================================================================================
class Path:

    @staticmethod
    def resource_path(relative_path):

        try:

            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


def output_name_name(name, output_name):

    txt_title1 = name
    txt_title2 = txt_title1.split("/")
    txt_title3 = txt_title2[-1]
    name_1 = txt_title3.split('/')[-1]
    name_2 = name_1.split('.')[0]
    name = output_name + '/' + name_2 + '.mp3'
    path_4 = os.path.isfile(name)

    if path_4 == True:
        return 'Se Encuentra'

    else:
        return '/' + name_2 + '.mp3'

##====================================================================================
# WORKER CON QTHREAD (ESTABLE)
##====================================================================================
class ConvertirAMP3Worker(QThread):
    progreso = pyqtSignal(int, int)  # actual, total
    completado = pyqtSignal(str)
    error = pyqtSignal(str)
    cancelado = pyqtSignal()
    
    def __init__(self, rutas, carpeta_salida):
        super().__init__()

        self.rutas = rutas
        self.carpeta_salida = carpeta_salida
        self._is_canceled = False
        
    def cancelar(self):

        self._is_canceled = True
        print("[CANCELAR] Señal de cancelación recibida")
        
    def run(self):

        try:
            total = len(self.rutas)
            
            for index, i in enumerate(self.rutas):

                # Verificar cancelación ANTES de procesar cada archivo
                if self._is_canceled:
                    print("[WORKER] Cancelación detectada, terminando...")
                    self.cancelado.emit()
                    return
                
                # Emitir progreso
                self.progreso.emit(index + 1, total)
                
                path_1 = Path.resource_path(i)
                path_2 = Path.resource_path(self.carpeta_salida)
                mp3_file = output_name_name(path_1, self.carpeta_salida)

                if mp3_file == 'Se Encuentra':

                    print(f"[WORKER] Archivo ya existe, saltando: {i}")
                    continue
                else:

                    path_3 = Path.resource_path(path_2 + mp3_file)
                    print(f"[WORKER] Procesando: {i} -> {path_3}")
                    
                    videoclip = VideoFileClip(path_1)
                    audioclip = videoclip.audio
                    audioclip.write_audiofile(path_3)
                    audioclip.close()
                    videoclip.close()
                    print(f"[WORKER] Completado: {path_3}")
            
            self.completado.emit("He Finalizado Exitosamente")
            
        except Exception as e:
            print(f"[WORKER] Error: {e}")
            self.error.emit(str(e))

# ============================================================
# DIALOG PERSONALIZADO
# ============================================================
class ProgressDialog(QDialog):

    def __init__(self, total, parent=None):

        super().__init__(parent)
        self.total = total
        self._is_canceled = False
        self.init_ui()
        
    def init_ui(self):

        self.setWindowTitle("Convirtiendo a MP3...")
        self.setFixedSize(400, 120)
        
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        self.label = QLabel(f"Procesando 0 de {self.total}...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #00eaff; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, self.total)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00c3ff;
                border-radius: 5px;
                background-color: #0a0a0f;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007c99, stop:1 #00eaff
                );
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)
        
        self.btn_cancelar = QBtn("Cancelar")
        self.btn_cancelar.setFixedHeight(40)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #101820;
                color: #00eaff;
                border: 2px solid #00c3ff;
                border-radius: 7px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00c3ff;
                color: #071018;
            }
        """)
        self.btn_cancelar.clicked.connect(self.cancelar)
        layout.addWidget(self.btn_cancelar, alignment=Qt.AlignCenter)
        
        # Estilo del diálogo        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                border: 2px solid #00c3ff;
                border-radius: 10px;
            }
        """)
        
    def cancelar(self):

        print("[DIALOG] Botón cancelar presionado")
        self._is_canceled = True
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.setText("Cancelando...")
        
    def set_progreso(self, actual, total):

        self.progress.setValue(actual)
        self.label.setText(f"Procesando {actual} de {total}...")
        
    def is_canceled(self):

        return self._is_canceled

##====================================================================================
# Clase Principal (El Soft-Ware)
##====================================================================================
class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init_ui()
        
    def init_ui(self):

        self.setWindowTitle('"MP4" Converter to: "MP3"')
        self.setFixedSize(275, 150)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #1f538d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2d6ca8;
            }
            QPushButton:pressed {
                background-color: #14375a;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(layout)
        
        btn_convertir = QPushButton("De MP4 a MP3")
        btn_convertir.setFixedSize(200, 40)
        btn_convertir.clicked.connect(self.de_mp4_a_mp3)
        layout.addWidget(btn_convertir, alignment=Qt.AlignCenter)
        
        try:
            ico_app = Path.resource_path('ico\\mp3.ico')
            self.setWindowIcon(QIcon(ico_app))
        except:
            pass
        
        self.center_window()
        
    def center_window(self):

        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
        
    def de_mp4_a_mp3(self):

        reply = QMessageBox.information(self, "Info",
            "Procede a Buscar un Archivo MP4, para Transformarlo a MP3...\nMuchas Gracias.",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            QMessageBox.warning(self, "Error...", "Cancelaste la Busqueda de Medios (MP4).")
            return
            
        path_input, _ = QFileDialog.getOpenFileNames(self, "Open File - *.MP4", "/gui/desktop",
            "Archivos de MP4 (*.mp4);;Todos los archivos (*.*)"
        )
        
        print('filePath |Ubicación| video: ', f'{path_input}\n')
        
        if not path_input:
            QMessageBox.warning(self, "Error...", "Cancelaste la Busqueda de Medios (MP4).")
            return
            
        reply2 = QMessageBox.information(self, "Info",
            "Procede a Buscar una Ubicación donde Alojar los Archivos MP3...\nMuchas Gracias.",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if reply2 == QMessageBox.Cancel:
            QMessageBox.warning(self, "Error...", "Cancelaste la Busqueda de Medios (MP4).")
            return
            
        path_output = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Salida", "/gui/desktop"
        )
        
        print('filePath |Salida| Audio: ', path_output, '\n')
        
        if not path_output:
            QMessageBox.warning(self, "Error...", "Cancelaste la Ubicación de Salida para el Archivo (MP3).")
            return
            
        files = len(path_input)
        reply3 = QMessageBox.information(self, "Info",
            f"Comenzare a Trabajar en:\nlos {files}, Archivos Seleccionados.\nFavor de dar tiempo.\nHasta que salga el aviso que he terminado.\nMuchas Gracias...",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if reply3 == QMessageBox.Cancel:
            QMessageBox.warning(self, "Error...", "Cancelaste la Conversión a (MP3).")
            return
            
        self._iniciar_conversion(path_input, path_output)
        
    def _iniciar_conversion(self, rutas, carpeta_salida):

        total = len(rutas)

        self.progress_dialog = ProgressDialog(total, self)
        self.progress_dialog.show()
        QCoreApplication.processEvents()

        self.worker = ConvertirAMP3Worker(rutas, carpeta_salida)

        self.worker.progreso.connect(self._actualizar_progreso)
        self.worker.completado.connect(self._conversion_completada)
        self.worker.error.connect(self._conversion_error)
        self.worker.cancelado.connect(self._conversion_cancelada)

        # Conectar el botón cancelar al worker
        self.progress_dialog.btn_cancelar.clicked.connect(self.worker.cancelar)
        
        self.worker.start()
        
    def _actualizar_progreso(self, actual, total):

        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.set_progreso(actual, total)
            QCoreApplication.processEvents()
        
    def _conversion_completada(self, mensaje):

        self.progress_dialog.close()
        
        carpeta_salida = self.worker.carpeta_salida

        try:
            output_file = os.listdir(carpeta_salida)
            
            for salida in output_file:
                if salida.endswith(".mp3"):

                    dir_songs_1 = carpeta_salida + '/' + salida
                    dir_songs = Path.resource_path(dir_songs_1)
                    print('filePath |Salida Audio| Extraido: ', dir_songs, '\n')

        except Exception as e:
            print(f"Error listando archivos: {e}")
        
        QMessageBox.information(self, "Info", f"{mensaje} Muchas Gracias por la Espera...")
        
    def _conversion_error(self, error_msg):

        self.progress_dialog.close()
        QMessageBox.warning(self, "Error...", f"{error_msg}")
        
    def _conversion_cancelada(self):

        self.progress_dialog.close()
        QMessageBox.information(self, "Info", "Conversión cancelada por el usuario.")

    # ============================================================
    # MÉTODOS DE COPIAR AL PORTAPAPELES, LA IMAGEN CON CRTL+C, CERRAR APP, (ATRAS -|- ADELANTE)
    # ============================================================
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close()
##====================================================================================
# Main App (El Innicio y Final de la APP)
##====================================================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
##====================================================================================
##====================================================================================