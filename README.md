# MyAnimeManager 3

La continuation de MyAnimeManager1 et MyAnimeManager2.

![](docs/imgs/2022-10-28-01-43-43.png)

Commencé en 2018.

## Dépendences
- python
- python-qt5
- peewee

## Lancement simple sans instalation

```sh
python3 src/MyAnimeManager3.py
```

## Migration des données de MyAnimeManager2 vers MyAnimeManager3
Pour migrer depuis la version 2, il est possible d'éxecuter un script qui va reprendre toutes les données et les migrer sur la nouvelle version:

```sh
python3 src/migrate_myanimemanager_v2_to_v3.py
```

Pour le moment, la configuration est à faire dans le fichier du script.

## Compilation & Installation

### Archlinux / Manjaro

```sh
make archlinux-build
make archlinux-install
```

### Windows

Installer: git, nsis, Python3, PyInstaller (```pip install pyinstaller```)
Ensuite: ```pip install -r requirements.txt```

Depuis la racine du projet:
.\packaging\windows\build.bat