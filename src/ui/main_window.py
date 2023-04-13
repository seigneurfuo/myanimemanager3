import os
import webbrowser

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

import database

# Onglets
from ui.tabs.planning_tab import PlanningTab
from ui.tabs.full_list_tab import FullListTab
from ui.tabs.list2_tab import List2
from ui.tabs.tools_tab import ToolsTab
from ui.tabs.stats_tab import StatsTab

# Dialogues
from ui.dialogs.about import AboutDialog
from ui.dialogs.collection_problems import CollectionProblemsDialog
from ui.dialogs.database_history import DatabaseHistoryDialog
from ui.dialogs.profiles_manage import ProfilesManageDialog
from ui.dialogs.settings import SettingsDialog

from db_backups_manager import DBBackupsManager
from exports import export_planning_to_csv

import core
import utils

class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=None)
        self.parent = parent
        self.app_dir = parent.app_dir

        self.tabs = tuple()

        self.init_ui()
        self.init_events()

        # On met à jour les informations sur l'onglet charger en premier
        self.update_tab_content(self.tabWidget.currentIndex())

    def init_ui(self):
        loadUi(os.path.join(os.path.dirname(__file__), "main_window.ui"), self)

        # Onglet 1 - Planning
        self.planning_tab = PlanningTab(self)
        self.planning_tab_layout.addWidget(self.planning_tab)

        # Onglet 2 - Liste des animés
        self.full_list_tab = FullListTab(self)
        self.full_list_tab_layout.addWidget(self.full_list_tab)

        # Onglet 3 - Liste des animés 2
        self.list2_tab = List2(self)
        self.list2_tab_layout.addWidget(self.list2_tab)

        # Onglet 4 - Outils
        self.tools_tab = ToolsTab(self)
        self.tools_tab_layout.addWidget(self.tools_tab)

        # Onglet 5 - Statistiques
        self.stats_tab = StatsTab(self)
        self.stats_tab_layout.addWidget(self.stats_tab)

        # Remplissage de la liste des onglets
        self.tabs = (self.planning_tab, self.full_list_tab, self.list2_tab, self.tools_tab, self.stats_tab)

        # Onglet par défaut
        self.tabWidget.setCurrentIndex(0)  # TODO: Configuration

    def init_events(self):
        # Menus
        self.open_profile_action.triggered.connect(self.when_menu_action_open_profile_clicked)
        self.planning_export_action.triggered.connect(self.when_menu_action_planning_export_clicked)
        self.about_action.triggered.connect(self.when_menu_action_about_clicked)
        self.bug_report_action.triggered.connect(self.when_menu_action_bug_report_clicked)
        self.check_problems_action.triggered.connect(self.when_menu_action_check_collection_clicked)
        self.open_database_backups_action.triggered.connect(self.when_menu_action_open_database_backups_clicked)
        self.manage_profiles_action.triggered.connect(self.when_menu_action_manage_profiles_clicked)
        self.open_settings_action.triggered.connect(self.when_menu_action_settings_clicked)

        # ----- Clic sur les onglets -----
        self.tabWidget.currentChanged.connect(self.when_current_tab_changed)

    # TODO: evenement lors du click sur un onglet

    # print(self.parent_qapplication.profile.get_series())

    def when_current_tab_changed(self, tab_index):
        """
        Fonction qui est appelée lorsqu'un onglet est cliqué
        Il permet de lancer la fonction when_visible qui déclanche divers actions (MAJ de l'affichage, ...)
        dans l'onglet concerné

        :param tab_index: Index de l'onglet cliqué 0 à x
        :return: None
        """

        self.update_tab_content(tab_index)

    def update_tab_content(self, tab_index):
        if tab_index != -1 and tab_index < len(self.tabs) and self.tabs[tab_index] is not None:
            self.tabs[tab_index].when_visible()

    def when_menu_action_open_profile_clicked(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.parent.profile.path))

    def when_menu_action_planning_export_clicked(self):
        filepath = export_planning_to_csv(self.parent.profile.path)

        # Bouton pour ouvrir le dossier ?
        QMessageBox.information(self, self.tr("Export terminé"),
                                self.tr("Le fichier a été généré ici:") + "\n    " + filepath,
                                QMessageBox.Ok)

    def when_menu_action_check_collection_clicked(self):
        messages = utils.get_collection_problems()
        dialog = CollectionProblemsDialog(messages)
        dialog.exec()

    def when_menu_action_about_clicked(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def when_menu_action_bug_report_clicked(self):
        webbrowser.open_new(core.bugtracker_url)

    def when_menu_action_open_database_backups_clicked(self):
        dialog = DatabaseHistoryDialog(self)
        dialog.exec()

        if dialog.selected_backup:
            QMessageBox.information(
                self, self.tr("Base de données restaurée"),
                self.tr(
                    "Le logiciel va se fermer. Veuillez le relancer pour que les modifications soient prises en compte"),
                QMessageBox.Ok)
            self.close()

    def when_menu_action_manage_profiles_clicked(self):
        profiles_manage = ProfilesManageDialog(ProfilesManageDialog.roles.manage, self.parent.profile)
        profiles_manage.exec()

    def when_menu_action_settings_clicked(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()

    def backup_database_before_quit(self):
        db_backups_manager = DBBackupsManager(self)
        db_backups_manager.backup_current_database()

    def closeEvent(self, a0):
        database.database.commit()
        self.backup_database_before_quit()

        super().close()
