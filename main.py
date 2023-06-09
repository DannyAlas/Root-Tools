import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIcon, QPixmap
import os
from base64 import b64decode
from tools.ccf_tools import CCF_Tools
from tools.win2bin import Wav2Bin
import importlib
import subprocess

class MainApp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Root Tools')
        data_uri = "data:image/png;base64,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"
        _, encoded = data_uri.split("base64,", 1)
        data = b64decode(encoded)
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.icon = QIcon(pixmap)
        self.setWindowIcon(self.icon)
        self.window_width, self.window_height = 1200, 900
        self.resize(self.window_width, self.window_height)
        self.setStyleSheet("""
			QWidget {
				font-size: 15px;
			}
			QComboBox {
				width: 160px;
			}
			QPushButton {
				width: 200px;
			}
            QMessageBox {
                font-size: 15px;
                align: center;
            }
            QTreeView::item {
                height: 25px;
            }
            QTreeView::item:selected {
                background-color: #5E5E5E;
            }
            QTreeView::item:hover {
                background-color: #3D3D3D;
            }
		""")
        
        # create a folder to store the data in the user's documents folder
        self.data_folder = os.path.join(os.path.expanduser('~'), 'Documents', 'root_tools')
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)
            # set the working directory to the data folder
        os.chdir(self.data_folder)
        
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout()
        self.central_widget.setLayout(self.layout)

        self.tab_widget = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tab_widget, 0, 0, 1, 2)

        # instanciate a status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setSizeGripEnabled(False)


        # add a tab for the ccf widget
        self.ccf_tab = CCF_Tools(self)
        self.tab_widget.addTab(self.ccf_tab, 'CCF')
        self.wav2bin_tab = Wav2Bin(self)
        self.tab_widget.addTab(self.wav2bin_tab, 'Wav2Bin')

        # when a user clicks on the tab, check if the required packages are installed
        self.tab_widget.currentChanged.connect(self.checkRequiredPackages)
        
        self.ccf_tab.initUi()


    def checkRequiredPackages(self):
        # check if the required packages are installed
        missing_packages = []
        # get the active tab
        active_tab = self.tab_widget.currentWidget()
        
        for package in active_tab.required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        if missing_packages:
            msg = QtWidgets.QMessageBox()
            # set the message box layout
            msg.setWindowTitle("Missing Packages")
            msg.setWindowIcon(self.icon)
            msg.setText(f"The following packages are required to run this tool: \n{', '.join(missing_packages)}")

            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            # button to install the packages
            install_button = msg.addButton('Install', QtWidgets.QMessageBox.ButtonRole.ActionRole)
            msg.addButton('Cancel', QtWidgets.QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            if msg.clickedButton() == install_button:
                self.installMissingPackages(missing_packages)

    def installMissingPackages(self, missing_packages: list):
        # creates a new process to install the missing packages in a window that shows the progress
        self.install_window = QtWidgets.QWidget()
        self.install_window.setWindowTitle('Installing Packages')
        self.install_window.setWindowIcon(self.icon)

        self.install_window.layout = QtWidgets.QVBoxLayout()
        self.install_window.setLayout(self.install_window.layout)
        self.install_window_progress_bar = QtWidgets.QProgressBar()
        self.install_window_progress_bar.setRange(0, len(missing_packages))
        self.install_window_progress_bar.setValue(0)
        self.install_window.layout.addWidget(self.install_window_progress_bar)
        self.install_window_label = QtWidgets.QLabel()
        self.install_window.layout.addWidget(self.install_window_label)
        self.install_window.show()
        self.install_window.raise_()
        self.install_window.activateWindow()
        self.install_window.setFocus()
        # a label that displays terminal output
        self.install_window_status_label = QtWidgets.QLabel()
        self.install_window.layout.addWidget(self.install_window_status_label)
        self.install_window_status_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.install_window_status_label.setWordWrap(True)
        self.install_window_status_label.setFixedHeight(100)
        self.install_window_status_label.setFixedWidth(300)
        self.install_window_status_label.setStyleSheet('background-color: #3D3D3D; color: #FFFFFF;')
        self.install_window_status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.install_window_status_label.setText('Installing packages...')
        # a button to close the window
        self.install_window_close_button = QtWidgets.QPushButton()
        self.install_window.layout.addWidget(self.install_window_close_button)
        self.install_window_close_button.setText('Close')
        self.install_window_close_button.clicked.connect(self.install_window.close)
        # a button to cancel the installation
        
        # capture the terminal output
        sys.stdout = 

        self.install_thread = QtCore.QThread()
        self.install_worker = InstallPackages(missing_packages, self.install_window_progress_bar, self.install_window_label)
        self.install_worker.moveToThread(self.install_thread)
        self.install_thread.started.connect(self.install_worker.run)
        self.install_worker.finished.connect(self.install_thread.quit)
        self.install_worker.finished.connect(self.install_window.close)
        self.install_thread.start()

    def normalOutputWritten(self, text):
        # append text to the QTextEdit
        print("AHHH", text)
        cursor = self.install_window_status_label.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.install_window_status_label.setTextCursor(cursor)
        self.install_window_status_label.ensureCursorVisible()
        
    def closeEvent(self, event):
        # when the user closes the window, close all the tabs
        for i in range(self.tab_widget.count()):
            self.tab_widget.widget(i).close()
        event.accept()
            
        
class InstallPackages(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    def __init__(self, missing_packages, progress_bar, label):
        super().__init__()
        self.missing_packages = missing_packages
        self.progress_bar = progress_bar
        self.label = label
        self.progress_bar.setRange(0, len(self.missing_packages))
        self.progress_bar.setValue(0)
        self.label.setText(f'Installing {self.missing_packages[0]}')

    def run(self):
        for package in self.missing_packages:
            self.label.setText(f'Installing {package}')

            self.process = subprocess.Popen([sys.executable, '-u', '-m', 'pip', 'install', package], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.finished.emit()

    def close(self):
        # stop the subprocess
        self.process.terminate()
        self.finished.emit()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    my_app = MainApp()
    app.setStyle('Fusion')
    my_app.show()
    sys.exit(app.exec())
                           

