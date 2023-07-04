import os

import database

DATABASE_NAME = "database.sqlite3"


def load_or_create_database(profile):
    database_path = os.path.join(profile.path, DATABASE_NAME)
    print("Database path:", database_path)

    # Génération des tables
    if not os.path.exists(database_path):
        database.database.init(database_path)

        tables = [database.Series, database.Seasons, database.SeasonsTypes, database.Planning, database.Friends,
                  database.FriendsPlanning]
        database.database.create_tables(tables)

        populate_tables()

    else:
        database.database.init(database_path)
        populate_tables()  # On laisse ça si MAJ

    return database_path


def populate_tables():
    populate_seasons_types()

    database.database.commit()

# FIXME: Pas propre, trouver comment corrriger ça
def populate_seasons_types():
    seasons_types = [
        {"sort_id": 1, "name": "Episodes"},
        {"sort_id": 2, "name": "Film"},
        {"sort_id": 3, "name": "OAV / OVA"},
        {"sort_id": 4, "name": "Specials / Bonus"},
    ]

    for index, seasons_type_data in enumerate(seasons_types):
        season_type_id = index + 1
        season_type = database.SeasonsTypes.get_or_none(database.SeasonsTypes.id == season_type_id)

        # Si existe pas, on crée, sinon on fait une MAJ
        if not season_type:
            season_type = database.SeasonsTypes()

        season_type.name = seasons_type_data["name"]
        season_type.sort_id = seasons_type_data["sort_id"]
        season_type.save()
