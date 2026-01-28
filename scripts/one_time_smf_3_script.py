import json
import ast
import os
import sqlalchemy

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

winners_list = [
    "Jens8",
    "ena1337_",
    "Denis_SMOG",
    "Forkxx",
    "Fasez",
    "do0mtrain",
    "SitioGO",
    "xHyui",
    "raynor88"
]

participants_list = [
    "DanGerPeru",
    "Rayna_Cruz",
    "E8Orc",
    "MisterWInner",
    "Jinvvar",
    "NorthDrakkar",
    "LunaStyle",
    "CrosSwc3",
    "kuhhhdark",
    "ProstT",
    "BFRjonathan",
    "Ighigo960",
    "OldGreggg",
    "lnSaNe17",
    "Claydsito",
    "Meftly",
    "Rihanna",
    "psjwandao",
    "TaroW3",
    "ThaGrinchyUNO",
    "Brkapro",
    "RN_Normyy",
    "ElusireiHarasses",
    "Rezunn",
    "GereOrcBaby",
    "KaGeManz",
    "brich8",
    "Snolecram",
    "Mikauzora",
    "Reklewt",
    "solstice1221",
    "Moghul",
    "Silentyoda",
    "GeneCoder",
    "Park9",
    "bfsStarscream",
    "Hypareal",
    "4peongold",
    "Crispy_Jenkins",
]

for winner in winners_list:
    added_points = 150
    name = winner
    old_val = dbsession.exec_driver_sql(f"SELECT total_points FROM participants2026 WHERE name = '{name}';").one_or_none()
    if old_val is None:
        new_val = 0 + added_points
        dbsession.exec_driver_sql(f"UPDATE participants2026 set total_points = {new_val} WHERE name = '{name}';")
        dbsession.commit()
    else:
        new_val = old_val.total_points + added_points
        dbsession.exec_driver_sql(f"UPDATE participants2026 set total_points = {new_val} WHERE name = '{name}';")
        dbsession.commit()

for participant in participants_list:
    added_points = 50
    name = participant
    old_val = dbsession.exec_driver_sql(f"SELECT total_points FROM participants2026 WHERE name = '{name}';").one_or_none()
    if old_val is None:
        new_val = 0 + added_points
        dbsession.exec_driver_sql(f"UPDATE participants2026 set total_points = {new_val} WHERE name = '{name}';")
        dbsession.commit()
    else:
        new_val = old_val.total_points + added_points
        dbsession.exec_driver_sql(f"UPDATE participants2026 set total_points = {new_val} WHERE name = '{name}';")
        dbsession.commit()
