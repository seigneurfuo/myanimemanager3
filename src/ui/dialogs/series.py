import os

from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.uic import loadUi


class SeriesDialog(QDialog):
    def __init__(self, serie):
        super(SeriesDialog, self).__init__()

        #self.parent = parent
        self.serie = serie

        self.init_ui()
        self.init_events()


    def init_ui(self):
        loadUi(os.path.join(QDir.currentPath(), 'ui/dialogs/series.ui'), self)

        #if self.serie:
            #self.seriemodal.setWindowTitle(self.serie.name)


    def init_events(self):
        pass


    def accept(self):
        self.serie.name = self.lineEdit_2.text()
        self.serie.sort_id = self.spinBox.value()

        super(SeriesDialog, self).accept()


    def reject(self):
        super(SeriesDialog, self).reject()