#!/bin/env python3

import os
from datetime import datetime

import peewee
from PyQt5.QtGui import QIcon, QColor

import utils

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QCheckBox, QHeaderView, QMessageBox
from PyQt5.uic import loadUi

from database import Series, Seasons, Friends, Planning, FriendsPlanning
from common import SEASONS_STATES, display_view_history_dialog


class List2(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.current_season_id = None

        self.init_ui()
        self.init_events()

    def init_ui(self):
        loadUi(os.path.join(os.path.dirname(__file__), "list2_tab.ui"), self)

    def init_events(self):
        self.pushButton.clicked.connect(self.when_export_button_clicked)
        self.pushButton_2.clicked.connect(self.when_show_view_history_button_clicked)
        self.tableWidget.currentCellChanged.connect(self.when_current_cell_changed)

    def when_visible(self):
        self.fill_data()

    def when_current_cell_changed(self):
        self.update_current_season_id()

    def update_current_season_id(self):
        current_item = self.tableWidget.item(self.tableWidget.currentRow(), 0)
        self.current_season_id = current_item.data(Qt.UserRole) if current_item else None

    def when_show_view_history_button_clicked(self):
        if self.current_season_id:
            display_view_history_dialog(self.current_season_id)

    def fill_data(self):
        today_date_object = datetime.now()

        data = Seasons().select().where(Seasons.is_deleted == 0).join(Series)\
            .order_by(Seasons.serie.sort_id, Seasons.serie.name, Seasons.sort_id, Seasons.name)

        row_count = len(data)

        self.label.setText(self.tr("Nombre d'éléments: ") + str(row_count))
        self.tableWidget.setRowCount(row_count)

        for row_index, season in enumerate(data):
            ids = "{} - {}".format(season.serie.sort_id, season.sort_id)
            year = str(season.year) if season.year and str(season.year) != "None" else ""

            # Calcul de l'age
            if year:
                # Différence entre deux dates
                release_year_datetime_object = datetime.strptime(str(season.year), "%Y")
                age_diff = today_date_object.year - release_year_datetime_object.year
                age = "{} ans".format(age_diff)
            else:
                age = ""

            # TODO: icone de l'état de visonnage
            season_state = SEASONS_STATES[season.state]

            columns = [ids, season.serie.name, season.type.name, season.name, str(season.episodes), year,
                       age, season_state['name']]

            for col_index, value in enumerate(columns):
                # FIXME: Un peut crade

                if col_index == 7:
                    item = QTableWidgetItem(season_state["name"])
                    item.setIcon(
                        QIcon(os.path.join(os.path.dirname(__file__), "../../resources/icons/", season_state["icon"])))

                else:
                    item = QTableWidgetItem(value)
                    item.setToolTip(item.text())

                item.setData(Qt.UserRole, season.id)

                # Bandeau orangé pour les series avec un numéro temporaire
                if col_index == 0 and season.serie.sort_id == 0:
                    item.setBackground(QColor("#FCC981"))

                self.tableWidget.setItem(row_index, col_index, item)

            # En diffusion
            airing = self.tr("Oui") if season.airing else self.tr("Non")
            item = QTableWidgetItem(airing)

            if season.airing:
                item.setForeground(QColor("#039d09"))

            item.setToolTip(item.text())
            self.tableWidget.setItem(row_index, len(columns), item)

            # Nombre de visionnages
            item = QTableWidgetItem(str(season.view_count))
            item.setToolTip(item.text())
            self.tableWidget.setItem(row_index, len(columns) + 1, item)

            # Favoris
            favorite_checkbox = QCheckBox()
            favorite_checkbox.setEnabled(False)
            favorite_checkbox.setChecked(season.favorite)

            self.tableWidget.setCellWidget(row_index, len(columns) + 2, favorite_checkbox)

            # Amis
            friends = [friend.name for friend in
                       Friends.select(Friends.name).where(Seasons.id == season.id).join(FriendsPlanning)
                       .join(Planning).join(Seasons).group_by(Friends.name)]

            item = QTableWidgetItem(", ".join(friends))
            item.setToolTip(item.text())
            self.tableWidget.setItem(row_index, len(columns) + 3, item)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionResizeMode(self.tableWidget.columnCount() - 1,
                                                                 QHeaderView.ResizeToContents)

    def when_export_button_clicked(self):
        filepath = utils.export_qtablewidget(self.tableWidget, self.parent.parent.profile.path, "liste")
        # Bouton pour ouvrir le dossier ?
        QMessageBox.information(None, self.tr("Export terminé"),self.tr("Le fichier a été généré ici:") + "\n    " + filepath,
                                QMessageBox.Ok)
