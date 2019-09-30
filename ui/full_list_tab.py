#!/bin/env python3
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDir

import os

from database import Series, Seasons


class FullListTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self._init_ui()
        self._init_events()

        self._fill_series_combobox()

    def _init_ui(self):
        loadUi(os.path.join(QDir.currentPath(), 'ui/full_list_tab.ui'), self)


    def _init_events(self):
        self.comboBox.currentIndexChanged.connect(self._on_series_list_current_index_changed)
        # self.pushButton.clicked.connect(self._on_serie_edit)
        pass

    # region ----- Remplissage de la liste des saisons -----
    def _fill_season_list(self, serie):
        self.tableWidget.setRowCount(0)

        seasons = Seasons.select().where(Seasons.serie == serie.id_).order_by(Seasons.sort_id)
        self.label_2.setText(str(len(seasons)))

        self.tableWidget.setRowCount(len(seasons))

        for row_id, season in enumerate(seasons):
            self.tableWidget.setItem(row_id, 0, QTableWidgetItem(season.name))
            self.tableWidget.setItem(row_id, 1, QTableWidgetItem(season.name))
    # endregion

    # region ----- Remplissage de la liste des informations sur la série -----
    def _fill_serie_data(self, serie):
        fields = [(self.label_3, serie.name)]
        for field, value in fields:
            field.setText(value)

        self.plainTextEdit.setPlainText(serie.description)
    # endregion

    # region ----- Serie combobox -----
    def _fill_series_combobox(self):
        self.comboBox.clear()
        for serie in Series.select().order_by(Series.sort_id):
            self.comboBox.addItem(serie.name)

    def _on_series_list_current_index_changed(self, index):
        serie = Series.select().where(Series.name == self.comboBox.currentText()).get()
        self._fill_serie_data(serie)
        self._fill_season_list(serie)
    # endregion
