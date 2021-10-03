#!/bin/env python3
import platform

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QProgressBar
from PyQt5.uic import loadUi

import os

from ui.custom_calendar import CustomCalendar
from database import Planning, Seasons


class PlanningTab(QWidget):
    def __init__(self, parent, app_dir):
        super().__init__(parent)

        self.parent = parent
        self.app_dir = app_dir

        self.planning_calendar = QWidget()

        self.init_ui()
        self.init_events()

    def init_ui(self):
        loadUi(os.path.join(self.app_dir, 'ui/planning_tab.ui'), self)

        self.planning_calendar = CustomCalendar()
        self.planning_calendar.setCellsBackgroundColor(QColor(115, 210, 22, 50))
        self.horizontalLayout_42.insertWidget(0, self.planning_calendar, )

    def init_events(self):
        self.today_button.clicked.connect(self.when_today_button_clicked)
        self.planning_calendar.clicked.connect(self.fill_watched_table)

    def when_visible(self):
        # Coloration des jours sur le calendrier
        self.planning_calendar.dates = [record.date for record in Planning().select().order_by(Planning.date)]

        self.fill_watched_table()
        self.fill_to_watch_table()

    def fill_watched_table(self):
        """
        Fonction qui rempli la liste des épisodes vus
        :return:
        """

        # Nettoyage de la liste
        self.tableWidget_7.setRowCount(0)

        # Nettoyage du nombre d'épisodes vus pour cette date
        self.label_82.setText("")

        calendar_date = self.planning_calendar.selectedDate().toPyDate()

        planning_data_list = Planning().select().where(Planning.date == calendar_date).order_by(Planning.id)
        row_count = len(planning_data_list)
        self.label_82.setText(str(row_count))
        self.tableWidget_7.setRowCount(row_count)

        for col_index, planning_data in enumerate(planning_data_list):
            column0 = QTableWidgetItem(planning_data.season.serie.name)
            self.tableWidget_7.setItem(col_index, 0, column0)

            column1 = QTableWidgetItem(planning_data.season.name)
            self.tableWidget_7.setItem(col_index, 1, column1)

            column2 = QTableWidgetItem(str(planning_data.episode))
            self.tableWidget_7.setItem(col_index, 2, column2)

    def get_episodes_to_watch(self, season_state=2):
        return Seasons.select().where(Seasons.state == season_state, Seasons.watched_episodes < Seasons.episodes,
                                      Seasons.is_deleted == 0).order_by(Seasons.id)

    def fill_to_watch_table(self):
        """
        Fonction qui rempli la liste des épisodes à voir
        :return:
        """

        # Nettoyage de la liste
        self.tableWidget_6.setRowCount(0)

        episodes_to_watch = self.get_episodes_to_watch()
        self.tableWidget_6.setRowCount(len(episodes_to_watch))

        for col_index, row_data in enumerate(episodes_to_watch):
            # Série
            column0 = QTableWidgetItem(row_data.serie.name)
            self.tableWidget_6.setItem(col_index, 0, column0)

            # Saison
            column1 = QTableWidgetItem(row_data.name)
            self.tableWidget_6.setItem(col_index, 1, column1)

            # Episode
            next_episode_index = int(row_data.watched_episodes) + 1
            next_episode_text = "{} / {}".format(next_episode_index, row_data.episodes)
            column2 = QTableWidgetItem(next_episode_text)
            self.tableWidget_6.setItem(col_index, 2, column2)

            # Progression
            progress_bar = QProgressBar(self)
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(row_data.episodes)
            progress_bar.setValue(
                row_data.watched_episodes)  # Car si un film donc épisode 1 / 1 on à déja une barre à 100%

            # Style différent si on est sous Windows
            if platform.system() == "Windows":
                progress_bar.setStyleSheet("QProgressBar::chunk ""{""background-color: #2B65EC;""}")
                progress_bar.setAlignment(Qt.AlignCenter)

            self.tableWidget_6.setCellWidget(col_index, 3, progress_bar)

    def when_today_button_clicked(self):
        """Fonction qui ramène le calendrier à la date actuelle"""

        self.planning_calendar.setSelectedDate(QDate.currentDate())
        self.fill_watched_table()


"""
id: entrée unique dans le planning
date: 
serie_id: 
season_id: 
episode_id: 
"""
