#!/bin/env python3
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDir, Qt

import os
from pathlib import Path

from ui.dialogs.series import SeriesDialog
from ui.dialogs.deleted_elements_dialog import DeletedElementsDialog
from database import Series, Seasons, database


class FullListTab(QWidget):
    def __init__(self, parent, app_dir):
        super().__init__(parent)
        self._parent = parent
        self.app_dir = app_dir

        self.current_serie_id = None
        self.current_season_id = None

        self.init_ui()
        self.load_profile()

        self.fill_series_combobox()

        self.init_events()


    def init_ui(self):
        loadUi(os.path.join(self.app_dir, 'ui/full_list_tab.ui'), self)


    def load_profile(self):
        database_path = "database.sqlite3"

        # Creation du profil
        self.appDataFolder = os.path.join(Path.home(), ".myanimemanager3")

        if not os.path.exists(self.appDataFolder):
            # Création du dossier ./profile/covers qui créer en meme temps le dossier parent ./profile
            os.makedirs(self.appDataFolder)

        database_path = os.path.join(self.appDataFolder, database_path)
        print("Database path:", database_path)
        # Génération des tables
        if not os.path.exists(database_path):
            database.init(database_path)
            database.create_tables([Series, Seasons])

        else:
            database.init(database_path)


    def init_events(self):
        self.comboBox.currentIndexChanged.connect(self.on_series_list_current_index_changed)
        # self.pushButton.clicked.connect(self._on_serie_edit)
        self.tableWidget.currentItemChanged.connect(self.on_seasons_list_current_index_changed)

        # region ----- Boutons -----
        self.add_serie_button.clicked.connect(self.on_add_serie_button_clicked_function)
        self.delete_serie_button.clicked.connect(self.on_delete_serie_button_clicked_function)

        self.view_deleted_elements_button.clicked.connect(self.on_view_deleted_elements_button_clicked_function)
        # endregion

        # on force l'affichage de l'informaton pour la première série au lancement
        self.on_series_list_current_index_changed()


    # region ----- Serie combobox -----
    def fill_series_combobox(self):
        self.comboBox.clear()

        series = Series.select().where(Series.is_deleted == 0).order_by(Series.sort_id)
        for serie in series:
            print(serie.name, "id: ", serie.id_)
            self.comboBox.addItem(serie.name, userData=serie.id_)

        self.current_serie_id = self.comboBox.currentData()
    # endregion


    def on_series_list_current_index_changed(self):
        # ----- -----

        self.current_serie_id = self.comboBox.currentData()

        if self.current_serie_id:
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


    def on_add_serie_button_clicked_function(self):
        new_serie = Series()
        series_dialog = SeriesDialog(serie=new_serie, app_dir=self.app_dir)

        if series_dialog.exec_():
            series_dialog.serie.save()
            self.fill_series_combobox()


    def on_delete_serie_button_clicked_function(self):
        if self.current_serie_id:
            # ----- Supression des saisons -----
            serie = Series.get(Series.id_ == self.current_serie_id)
            serie.is_deleted = 1
            serie.save()

            #self.on_series_list_current_index_changed()
            self.fill_series_combobox()


    def on_view_deleted_elements_button_clicked_function(self):
        deleted_seasons = Seasons.select().where(Seasons.is_deleted == 1).order_by(Seasons.sort_id)
        dialog = DeletedElementsDialog(deleted_seasons=deleted_seasons, app_dir=self.app_dir)

        # TODO:
        if dialog.exec_():
            pass


    # region ----- Remplissage de la liste des saisons -----
    def fill_season_list(self, serie):
        self.tableWidget.setRowCount(0)

        seasons = Seasons.select().where(Seasons.serie == serie.id_).order_by(Seasons.sort_id)
        seasons_count = len(seasons)

        self.label_2.setText(str(seasons_count))

        self.tableWidget.setRowCount(seasons_count)
        for row_index, season in enumerate(seasons):
            columns = [season.seasons_type.name, season.name]

            print(columns)

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
        self.current_season_id = self.tableWidget.currentItem().data(Qt.UserRole)

        season = Seasons.select().where(Seasons.id_ == self.current_season_id).get()
        self.fill_season_data(season)

    # endregion
