#!/bin/env python3
import cgitb
import json
import sys
import os
import platform

from PyQt6.QtWidgets import QApplication
import core
import updater
from ui.dialogs.profiles_manage import ProfilesManageDialog

from ui.main_window import MainWindow
from database_manager import load_or_create_database
from profiles import Profiles

from common import load_settings
from ui.themes import set_theme


class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.app_dir = os.path.abspath(os.path.dirname(__file__))

        self.setApplicationName(core.app_name)
        self.setApplicationDisplayName(core.app_name_and_version)
        self.setApplicationVersion(core.app_version)

        # Patch pour avoir l'icone de la barre des tâches sous Windows
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        if platform.system() == "Windows":
            import ctypes
            app_id = f'{core.app_name}.{core.app_version}'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        self.profile = None
        self.database_path = None

        self.settings = load_settings()

        if core.app_version != "DEV" and self.settings['updates_check']:
            updater.check_for_update()

        # Définition du thême
        set_theme(self, self.settings["application_stylesheet"])

        self.profile = self.load_profile()
        self.database_path =  self.load_database()

        display_name = self.tr("{} - Profil: {}").format(core.app_name_and_version, self.profile.name)
        self.setApplicationDisplayName(display_name)

        mainwindow = MainWindow(self)
        mainwindow.center()
        mainwindow.showMaximized()

    def load_profile(self):
        # Creation des dossiers de l'applications
        if not os.path.isdir(core.PROFILES_PATH):
            os.makedirs(core.PROFILES_PATH)

        profiles_list = Profiles.get_profiles_list()

        # Si pas de profil ou bien plusieurs, on ouvre l'assistant
        if len(profiles_list) != 1:
            profiles_manage = ProfilesManageDialog(None, ProfilesManageDialog.roles.choose, None)
            profiles_manage.exec()

            if profiles_manage.selected_profile == None:
                exit(0)
            else:
                profile = profiles_manage.selected_profile

        else:
            # Creation du profil
            profile = profiles_list[0]

        return profile

    def load_database(self):
        return load_or_create_database(self.profile)

if __name__ == "__main__":
    import cgitb
    cgitb.enable(format='text')

    application = Application(sys.argv)
    sys.exit(application.exec())
