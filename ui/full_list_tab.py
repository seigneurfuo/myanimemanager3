#!/bin/env python3
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDir, Qt

import os

from database import Series, Seasons


class FullListTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.init_ui()

        self.current_serie_id = None
        self.current_season_id = None

        self.fill_series_combobox()

        self.init_events()

    def init_ui(self):
        loadUi(os.path.join(QDir.currentPath(), 'ui/full_list_tab.ui'), self)


    def init_events(self):
        self.comboBox.currentIndexChanged.connect(self.on_series_list_current_index_changed)
        # self.pushButton.clicked.connect(self._on_serie_edit)
        self.tableWidget.currentItemChanged.connect(self.on_seasons_list_current_index_changed)

        # region ----- Boutons -----
        self.delete_serie_button.clicked.connect(self.on_delete_serie_button_clicked)
        # endregion

        pass

    # region ----- Serie combobox -----
    def fill_series_combobox(self):
        self.comboBox.clear()

        series = Series.select().order_by(Series.sort_id)
        for serie in series:
            print(serie.name)
            self.comboBox.addItem(serie.name, userData=serie.id_)

    # endregion

    def on_series_list_current_index_changed(self, index):
        # ----- -----
        self.current_serie_id = self.comboBox.currentData()
        print(self.current_serie_id)

        serie = Series.select().where(Series.id_ == self.current_serie_id).get()
        self.fill_serie_data(serie)
        self.fill_season_list(serie)

    # region ----- Remplissage de la liste des informations sur la série -----
    def fill_serie_data(self, serie):
        fields = [(self.label_3, serie.name)]

        for field, value in fields:
            field.setText(value)

        # FIXME: Utiliser en fonction de la classe la bonne fonction ?
        self.plainTextEdit.setPlainText(serie.description)
    # endregion

    def on_delete_serie_button_clicked(self):
        # FIXME: Cascade SQL Delete

        # ----- Supression des saisons -----
        seasons = Seasons.select().where(Seasons.serie == self.current_serie_id).order_by(Seasons.sort_id)
        print([season.name for season in seasons])
        for season in seasons:
            Seasons.delete_by_id(season.id_)

        # ----- Supression de la série -----
        Series.delete_by_id(self.current_serie_id)

        self.fill_series_combobox()
        self.fill_serie_data()

    # region ----- Remplissage de la liste des saisons -----
    def fill_season_list(self, serie):
        self.tableWidget.setRowCount(0)

        seasons = Seasons.select().where(Seasons.serie == serie.id_).order_by(Seasons.sort_id)
        seasons_count = len(seasons)

        self.label_2.setText(str(seasons_count))

        self.tableWidget.setRowCount(seasons_count)
        for row_index, season in enumerate(seasons):
            columns = [season.seasons_type.name, season.name]

            for col_index, value in enumerate(columns):
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, season.id_)
                self.tableWidget.setItem(row_index, col_index, item)

    # endregion

    def fill_season_data(self, season):
        fields = [(self.label_8, season.name),
                  (self.label_10, season.date)]

        for field, value in fields:
            field.setText(value)

    def on_seasons_list_current_index_changed(self):
        row_id = self.tableWidget.currentRow()
        self.current_season_id = self.tableWidget.currentItem().data(Qt.UserRole)

        season = Seasons.select().where(Seasons.id_ == self.current_season_id).get()
        self.fill_season_data(season)

    # endregion
