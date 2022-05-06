#!/bin/env python3

import sys
import os

from pathlib import Path
from PyQt5.QtWidgets import QApplication

import database
import default_settings

from ui.main_window import MainWindow


class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.app_dir = os.path.abspath(os.path.dirname(__file__))
        self.name = "MyAnimeManager 3"
        self.version = "2022.05.06"
        self.description = self.tr("Un gestionnaire de séries multiplateforme écrit en Python3 et Qt5")

        self.setApplicationName(self.name)
        self.setApplicationDisplayName(self.name)
        self.setApplicationVersion(self.version)

        self.default_settings = default_settings.DEFAULT_SETTINGS
        self.profile_path = None
        self.season_states = [self.tr("Indéfinie"), self.tr("A voir"), self.tr("En cours"), self.tr("Terminée"),
                              self.tr("Annulée")]

        self.database_path = None
        self.load_profile()

        self.mainwindow = MainWindow(self)
        self.mainwindow.show()

    def load_profile(self):
        database_path = "database.sqlite3"

        # Creation du profil
        self.profile_path = os.path.join(Path.home(), ".myanimemanager3")

        if not os.path.exists(self.profile_path):
            # Création du dossier ./profile/covers qui créer en meme temps le dossier parent ./profile
            os.makedirs(self.profile_path)

        self.database_path = os.path.join(self.profile_path, database_path)
        print("Database path:", self.database_path)
        # Génération des tables
        if not os.path.exists(self.database_path):
            database.database.init(self.database_path)
            database.database.create_tables([database.Series, database.Seasons])

        else:
            database.database.init(self.database_path)


if __name__ == "__main__":
    application = Application(sys.argv)
    application.exec_()
