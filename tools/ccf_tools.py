from turtle import down
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json
from PyQt6 import QtWidgets, QtCore, QtGui
import re
import os
from PyQt6.QtCore import pyqtSignal, QObject
import pip
class StructureBase(BaseModel):
    id: int
    acronym: str
    name: str
    structure_id_path: List[int]
    volume: int
    rgb_triplet: List[int]
    graph_id: int
    graph_order: int
    structure_set_ids: List[int]
    

class StructureTreeBase(BaseModel):
    ccf_year: str
    name: str
    structure_sets: List[StructureBase]


class Structure(StructureBase):

    def toJSON(self):
        return {
            'id': self.id,
            'acronym': self.acronym,
            'name': self.name,
            'structure_id_path': self.structure_id_path,
            'volume': self.volume,
            'rgb_triplet': self.rgb_triplet,
            'graph_id': self.graph_id,
            'graph_order': self.graph_order,
            'structure_set_ids': self.structure_set_ids
        }
    

class StructureTree(QObject):
    downloading = pyqtSignal()
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, ccf_year: str, name: str, resolution: int = 10,cache_file: Optional[str] = None,  manifest: str = 'manifest.json'):
        super().__init__()
        self.ccf_year = ccf_year
        self.name = name
        self.structures = []
        self.resolution = resolution
        self.manifest = manifest

        if cache_file is not None and Path(cache_file).exists():
            self.cache_file = cache_file
            self.load()
        else:
            self.cache_file = None

    def toJSON(self):
        if type(self.structures) == dict:
            return {
            'ccf_year': self.ccf_year,
            'name': self.name,
            'structures': self.structures
            }
        else:
            return {
                'ccf_year': self.ccf_year,
                'name': self.name,
                'structures': [structure.toJSON() for structure in self.structures]
            }

    def load(self):
        try:
            with open(Path(self.cache_file), 'r') as f:
                data = json.load(f)
                self.ccf_year = data['ccf_year']
                self.name = data['name']
                self.structures = [Structure(**structure) for structure in data['structures']]
                self.rsp = ReferenceSpaceCache(int(self.resolution), f"annotation/ccf_{self.ccf_year}", manifest=self.manifest).get_reference_space(structure_file_name=self.cache_file)
        except:
            pass

    def loadNew(self): 

        self.downloading.emit()
        
        try:
            if self.cache_file is not None and Path(self.cache_file).exists():
                print('loading from cache')
                with open(Path(self.cache_file), 'r') as f:
                    data = json.load(f)
                    self.ccf_year = data['ccf_year']
                    self.name = data['name']
                    self.structures = [Structure(**structure) for structure in data['structures']]
                    self.rsp = ReferenceSpaceCache(int(self.resolution), f"annotation/ccf_{self.ccf_year}", manifest=self.manifest).get_reference_space()
            else:
                self.rsp = ReferenceSpaceCache(int(self.resolution), f"annotation/ccf_{self.ccf_year}", manifest=self.manifest).get_reference_space()
                id_name_map = self.rsp.structure_tree.get_name_map()

                for id, name in id_name_map.items():
                    self.structures.append(Structure(
                        id=id,
                        acronym=self.rsp.structure_tree.get_structures_by_id([id])[0]['acronym'],
                        name=name,
                        structure_id_path=self.rsp.structure_tree.get_structures_by_id([id])[0]['structure_id_path'],
                        volume=self.rsp.total_voxel_map[id] / 1000000,
                        rgb_triplet=self.rsp.structure_tree.get_structures_by_id([id])[0]['rgb_triplet'],
                        graph_id=self.rsp.structure_tree.get_structures_by_id([id])[0]['graph_id'],
                        graph_order=self.rsp.structure_tree.get_structures_by_id([id])[0]['graph_order'],
                        structure_set_ids=self.rsp.structure_tree.get_structures_by_id([id])[0]['structure_set_ids']
                    ))
        except Exception as e:
            self.error_message = str(e)
            self.error.emit(str(e))
            return

        self.save()
        
        self.finished.emit()

    

    def save(self):
        with open(f'structure_tree_{self.ccf_year}_{self.resolution}.json', 'w') as f:
            json.dump(self.toJSON(), f, indent=4)


class CCF_Tools(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QtWidgets.QGridLayout(self)
        self.required_packages = ['allensdk']

    def initUi(self):
        self.msg = None
        
        # allow user to select the desired reference space
        self.ref_space_label = QtWidgets.QLabel('Reference Space:')
        self.ref_space_combo = QtWidgets.QComboBox()
        self.ref_space_combo.addItems(['ccf_2017', 'ccf_2016', 'ccf_2015'])

        # resoultion of the reference space
        self.ref_space_res_label = QtWidgets.QLabel('Resolution:')
        self.ref_space_res_combo = QtWidgets.QComboBox()
        self.ref_space_res_combo.addItems(['10', '25', '50', '100'])

        # load the reference space
        self.load_ref_space_button = QtWidgets.QPushButton('Load Reference Space')
        self.load_ref_space_button.clicked.connect(self.loadNewReferenceSpace)

        # create a status bar
        self.status_bar = self.parent.statusBar()

        # create search bar
        self.search_bar_label = QtWidgets.QLabel('Search:')
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText('Search')
        self.search_bar.textChanged.connect(self.searchTree)

        self.structure_tree = QtWidgets.QTreeView()
        self.structure_tree.setUniformRowHeights(True)
        self.structure_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.structure_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.structure_tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # add all widgets to the layout
        self.layout.addWidget(self.ref_space_label, 0, 0)
        self.layout.addWidget(self.ref_space_combo, 0, 1)
        self.layout.addWidget(self.ref_space_res_label, 1, 0)
        self.layout.addWidget(self.ref_space_res_combo, 1, 1)
        # make the load reference space button span 2 columns
        self.load_ref_space_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.load_ref_space_button, 0, 2, 2, 2)
        # add a line between the reference space and the search bar
        self.line1 = QtWidgets.QFrame()
        self.line1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout.addWidget(self.line1, 2, 0, 1, 4)
        self.layout.addWidget(self.search_bar_label, 3, 0)
        self.layout.addWidget(self.search_bar, 3, 1, 1, 3)
        # add a line between the search bar and the tree
        self.line2 = QtWidgets.QFrame()
        self.line2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout.addWidget(self.line2, 4, 0, 1, 4)

        self.layout.addWidget(self.structure_tree, 5, 0, 1, 4)



        self.createTree()

    def searchTree(self):
        filter_text = self.search_bar.text()
        if filter_text != "":
            for i in range(self.structure_tree.model().rowCount()):
                if filter_text.lower() in self.structure_tree.model().item(i).text().lower() or any (filter_text.lower() in self.structure_tree.model().item(i).child(j).text().lower() for j in range(self.structure_tree.model().item(i).rowCount())):
                    
                    self.structure_tree.setRowHidden(i, self.structure_tree.rootIndex(), False)   
                    self.structure_tree.expand(self.structure_tree.model().index(i, 0))
                                
                else:
                    self.structure_tree.setRowHidden(i, self.structure_tree.rootIndex(), True)
        else:
            for i in range(self.structure_tree.model().rowCount()):
                self.structure_tree.collapse(self.structure_tree.model().index(i, 0))
            

    def createPopUp(self, message):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setText(message)
        self.msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        self.msg.setWindowTitle("Root Tools")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        self.msg.exec()

    def updatePopUp(self, message):
        if self.msg is None:
            self.createPopUp(message)
        elif self.msg.isVisible():
            self.msg.setText(message)
        else:
            self.msg.setText(message)
            self.msg.show()


    def createTree(self):
        # regex for a file name structure_tree_YYYY_numbers.json
        struct_tree_regex = re.compile(r'structure_tree_\d{4}_\d{1,2}.json')
        cache_file = ""
        for file in os.listdir(self.parent.data_folder ):
            if struct_tree_regex.match(file):
                print(file)
                cache_file = os.path.join(self.parent.data_folder, file)
                break
        
        if cache_file == "" or not os.path.exists(cache_file):
            self.status_bar.showMessage("No Cached Structure Tree Found.")
        else:
            self.struct_tree = StructureTree(cache_file=cache_file, ccf_year="2017", name="Mouse Brain Atlas", resolution=10, manifest='manifest.json')
            
            # use the dictionary to populate the structure tree
            self.structure_tree_model = QtGui.QStandardItemModel()
            self.structure_tree.setModel(self.structure_tree_model)
            # header to ccf_year
            self.structure_tree_model.setHorizontalHeaderLabels([f"CCF {self.struct_tree.ccf_year} - {self.struct_tree.resolution}um"])
            
            for struct in self.struct_tree.structures:
                # create a QStandardItem for each structure
                item = QtGui.QStandardItem(struct.name)
                # add a subitem with a label for the id
                item.appendRow(QtGui.QStandardItem(f'Id: {struct.id}'))
                item.appendRow(QtGui.QStandardItem(f"Acronym: {struct.acronym}"))
                item.appendRow(QtGui.QStandardItem(f"Volume mm\u00b3: {struct.volume}"))
                item.appendRow([QtGui.QStandardItem(f"Structure id path: {struct.structure_id_path}")])

                # add the item to the model
                self.structure_tree_model.appendRow(item)
                self.status_bar.showMessage('Loaded structure tree')


    def loadNewReferenceSpace(self):
        """
        Loads a new reference space from the AllenSDK and saves it to the data folder
        """

        self.thread = QtCore.QThread()

        file_name = f"structure_tree_{self.ref_space_combo.currentText().strip('ccf_')}_{self.ref_space_res_combo.currentText()}.json"
        
        if not os.path.exists(self.parent.data_folder) or os.listdir(self.parent.data_folder) == []:
            self.struct_tree  = StructureTree(ccf_year=self.ref_space_combo.currentText().strip("ccf_"), resolution=self.ref_space_res_combo.currentText(), name="Mouse Brain Atlas", manifest='manifest.json')
        else:
            for file in os.listdir(self.parent.data_folder):
                if file == file_name:
                    self.struct_tree = StructureTree(
                        cache_file=os.path.join(self.parent.data_folder, file), 
                        ccf_year=self.ref_space_combo.currentText().strip("ccf_"), 
                        resolution=self.ref_space_res_combo.currentText(), 
                        name="Mouse Brain Atlas", # TODO: make this a variable that can users can change
                        manifest='manifest.json'
                        )
                else:
                    self.struct_tree  = StructureTree(ccf_year=self.ref_space_combo.currentText().strip("ccf_"), resolution=self.ref_space_res_combo.currentText(), name="Mouse Brain Atlas", manifest='manifest.json')
        
        self.struct_tree.moveToThread(self.thread)
        
        self.thread.started.connect(lambda: self.status_bar.showMessage(f'Downloading structure tree for {self.struct_tree.ccf_year} - {self.struct_tree.resolution}um. This can take a while...'))
        self.thread.started.connect(lambda: self.updatePopUp(f'Downloading structure tree for {self.struct_tree.ccf_year} - {self.struct_tree.resolution}um. This can take a while...'))

        self.struct_tree.error.connect(lambda: self.status_bar.showMessage('Error downloading structure tree'))
        # the error is a string signal
        self.struct_tree.error.connect(lambda: self.updatePopUp(f'Error downloading structure tree {self.struct_tree.ccf_year} - {self.struct_tree.resolution}um.\n\n ERROR: \n{self.struct_tree.error_message}'))
        
        self.thread.started.connect(self.struct_tree.loadNew)
        self.struct_tree.finished.connect(self.thread.quit)
        self.struct_tree.finished.connect(self.struct_tree.deleteLater)
        self.struct_tree.finished.connect(lambda: self.status_bar.showMessage('Download Complete!'))
        self.struct_tree.finished.connect(lambda: self.updatePopUp(f'Download Complete!'))
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()


        self.struct_tree.finished.connect(self.createUnCahcedTree)

    def createUnCahcedTree(self):
    
        # use the dictionary to populate the structure tree
        self.structure_tree_model = QtGui.QStandardItemModel()
        self.structure_tree.setModel(self.structure_tree_model)
        # header to ccf_year
        self.structure_tree_model.setHorizontalHeaderLabels([f"CCF {self.struct_tree.ccf_year} - {self.struct_tree.resolution}um"])
        
        for struct in self.struct_tree.structures:
            # create a QStandardItem for each structure
            item = QtGui.QStandardItem(struct.name)
            # add a subitem with a label for the id
            item.appendRow(QtGui.QStandardItem(f'Id: {struct.id}'))
            item.appendRow(QtGui.QStandardItem(f"Acronym: {struct.acronym}"))
            item.appendRow(QtGui.QStandardItem(f"Volume mm\u00b3: {self.struct_tree.rsp.total_voxel_map[struct.id] / 1000000}"))

            # name = self.struct_tree.rsp.structure_tree.get_structures_by_id([id])[0]['name']

            structures_item = QtGui.QStandardItem(f"Structures" )
            # the structures are a list of structure ids in the order they appear in the structure tree
            last_st = None
            for i, id in enumerate(struct.structure_id_path):
                # get the name of the structure from the structure id
                name = self.struct_tree.rsp.structure_tree.get_structures_by_id([id])[0]['name']
                # create a QStandardItem for each structure
                st = QtGui.QStandardItem(f'{name}: {id}')
                # make it uneditable
                st.setEditable(False)
                # make it always expand
                st.setDropEnabled(False)
                
                # if we're at the first structure, add it to the item
                if i == 0:
                    structures_item.appendRow(st)
                # otherwise, add it to the last structure
                else:
                    last_st.appendRow(st)
                # set the last structure to the current structure
                last_st = st
            

            item.appendRow(structures_item)
                
            # add the item to the model
            self.structure_tree_model.appendRow(item)
            self.status_bar.showMessage('Loaded structure tree')


