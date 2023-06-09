import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QLineEdit, QPushButton, QGridLayout, QWidget, QLabel
from PyQt6.QtWidgets import QFileDialog, QWidget, QMessageBox

class Wav2Bin(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.required_packages = ['numpy', 'matplotlib', 'wave', 'pyqtgraph']

        self.layout = QGridLayout()
        self.centralWidget = self

        self.openFileButton = QPushButton("Open Wav File", self.centralWidget)
        self.openFileButton.clicked.connect(self.openFile)

        self.singleFileText = QLineEdit(self.centralWidget)
        self.singleFileText.setReadOnly(True)
        self.singleFileText.setPlaceholderText("Select a file to convert")

        self.saveFileButton = QPushButton("Save Bin File", self.centralWidget)
        self.saveFileButton.clicked.connect(self.saveFile)

        # batch process 
        # select a directory full of wav files
        # select a directory to save the binary files
        # convert all wav files to binary files
        self.selectBatchFolderButton = QPushButton("Select Batch Folder", self.centralWidget)
        # text area to display the selected 
        self.selectBatchFolderText = QLineEdit(self.centralWidget)
        self.selectBatchFolderText.setReadOnly(True)
        self.selectBatchFolderText.setPlaceholderText("Select a folder to batch process")
        self.selectBatchFolderButton.clicked.connect(self.selectBatchFolder)

        self.selectBatchSaveFolderButton = QPushButton("Select Batch Save Folder", self.centralWidget)
        # text area to display the selected
        self.selectBatchSaveFolderText = QLineEdit(self.centralWidget)
        self.selectBatchSaveFolderText.setReadOnly(True)
        self.selectBatchSaveFolderText.setPlaceholderText("Select a folder to save the batch processed files")
        self.selectBatchSaveFolderButton.clicked.connect(self.selectBatchSaveFolder)


        # run batch process
        self.runBatchProcessButton = QPushButton("Run Batch Process", self.centralWidget)
        self.runBatchProcessButton.setEnabled(False)
        self.runBatchProcessButton.clicked.connect(self.runBatchProcess)

        # a bottom widget to display a selected wav and binary file
        # a button to select a wav file
        # a button to select a binary file
        
                
        
        self.layout.addWidget(self.openFileButton, 0, 0)
        self.layout.addWidget(self.singleFileText, 0, 1)
        self.layout.addWidget(self.saveFileButton, 1, 0)
        self.layout.addWidget(self.selectBatchFolderButton, 2, 0)
        self.layout.addWidget(self.selectBatchFolderText, 2, 1)
        self.layout.addWidget(self.selectBatchSaveFolderButton, 3, 0)
        self.layout.addWidget(self.selectBatchSaveFolderText, 3, 1)
        self.layout.addWidget(self.runBatchProcessButton, 4, 0)
        
        self.centralWidget.setLayout(self.layout)



        self.binarySound = bytearray()
        self.binaryHeader = bytearray()

    def openFile(self) -> None:
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Wav Files (*.wav)")
        if fileName:
            with open(fileName, 'rb') as f:
                self.binaryHeader = f.read(44)
                self.binarySound = f.read()

            self.singleFileText.setText(fileName)

    def saveFile(self) -> None:
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Binary Files (*.bin)")
        if fileName:
            with open(fileName, 'wb') as f:
                f.write(self.binarySound)

                # inform the user that the file has been saved
                QMessageBox.information(self, "Success", "File saved successfully")

    def selectBatchFolder(self) -> None:
        folderName = QFileDialog.getExistingDirectory(self, "Select Batch Folder", "")
        if folderName:
            self.selectBatchFolderText.setText(folderName)

        if self.selectBatchFolderText.text() != "" and self.selectBatchSaveFolderText.text() != "":
            self.runBatchProcessButton.setEnabled(True)

    def selectBatchSaveFolder(self) -> None:
        folderName = QFileDialog.getExistingDirectory(self, "Select Batch Save Folder", "")
        if folderName:
            self.selectBatchSaveFolderText.setText(folderName)

        if self.selectBatchFolderText.text() != "" and self.selectBatchSaveFolderText.text() != "":
            self.runBatchProcessButton.setEnabled(True)

    def runBatchProcess(self) -> None:
        if self.selectBatchFolderText.text() == "" or self.selectBatchSaveFolderText.text() == "":
            QMessageBox.warning(self, "Warning", "Please select a folder and save folder")
        else:
            for fileName in os.listdir(self.selectBatchFolderText.text()):
                if fileName.endswith(".wav"):
                    with open(os.path.join(self.selectBatchFolderText.text(), fileName), 'rb') as f:
                        self.binaryHeader = f.read(44)
                        self.binarySound = f.read()
                        with open(os.path.join(self.selectBatchSaveFolderText.text(), fileName[:-4] + ".bin"), 'wb') as f:
                            f.write(self.binarySound)
            QMessageBox.information(self, "Success", "Batch process completed")

    def create_waveform_spectrum(self, wav_file: str, sample_rate: int):
        import wave
        import numpy as np # type: ignore
        import matplotlib.pyplot as plt # type: ignore
        import pyqtgraph as pg # type: ignore
        from pyqtgraph import PlotWidget, plot # type: ignore

        self.graphWidget = pg.MatplotlibWidget()

        signal_wave = wave.open(wav_file, 'r')
        sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
        sig = sig[:]

        plot_a = plt.subplot(211)
        plot_a.plot(sig)
        plot_a.set_xlabel('sample rate * time')
        plot_a.set_ylabel('energy')

        plot_b = plt.subplot(212)
        plot_b.specgram(sig, NFFT=1024, Fs=sample_rate, noverlap=900)
        plot_b.set_xlabel('Time')
        plot_b.set_ylabel('Frequency')


    