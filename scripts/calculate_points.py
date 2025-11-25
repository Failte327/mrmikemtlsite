import json
import ast
import os
import sqlalchemy

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

# CALCULATE POINTS CODE
query = dbsession.exec_driver_sql(f"SELECT name, participants FROM tournaments;")
for record in query.all():
    participants = ast.literal_eval(record.participants)
    print(f"Calculating results for {record.name}...")
    for name, placement in participants.items():
        participants_table_query = dbsession.exec_driver_sql(f"SELECT name FROM participants where name = '{name}';")
        if placement is None:
            added_points = 0
        elif placement == 1:
            added_points = 100
        elif placement == 2:
            added_points = 70
        elif placement <= 4:
            added_points = 40
        elif placement <= 8:
            added_points = 25
        elif placement <= 16:
            added_points = 15
        else:
            added_points = 10
        old_val = dbsession.exec_driver_sql(f"SELECT total_points FROM participants WHERE name = '{name}';").one_or_none()
        if old_val is None:
            new_val = 0 + added_points
            dbsession.exec_driver_sql(f"UPDATE participants set total_points = {new_val} WHERE name = '{name}';")
            dbsession.commit()
        else:
            new_val = old_val.total_points + added_points
            dbsession.exec_driver_sql(f"UPDATE participants set total_points = {new_val} WHERE name = '{name}';")
            dbsession.commit()
