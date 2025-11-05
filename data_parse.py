import json
import ast
import os
import sqlalchemy

dbsession = sqlalchemy.create_engine("sqlite:///smf_tournaments_database.sqlite3").connect()


# CODE FOR PARSING TOURNAMENTS_DATA.JSON
# tournaments = []
# with open("tournaments_data.json", "r") as data_file:
#     data = json.load(data_file).get("data")

#     for tournament in data:
#         tournament_id = tournament.get("id")
#         tournament_name = tournament.get("attributes").get("name").replace(" ", "_")
#         new_file = open(f"{tournament_name}-{tournament_id}.json", "x")
#         new_file.close()
#         tournaments.append(tournament_id)

#     print(tournaments)

files = os.listdir("in_progress/")

# PARSE AND CATALOG DATA FROM TOURNAMENT RECORD
# for file in files:
#     with open(f"in_progress/{file}", "r") as raw_data:
#         data = json.load(raw_data).get("data")
#         participants = {}
#         name = file.strip(".json")
#         for participant in data:
#             if participant is not None:
#                 attributes = participant.get("attributes")
#                 if participant.get("relationships").get("user"):
#                     participant_id = participant.get("relationships").get("user").get("id")
#                     username = attributes.get("username")
#                     placement = attributes.get("final_rank")
#                     participants[username] = placement

#         stringified_dict = str(participants)
#         dbsession.exec_driver_sql(f"INSERT INTO tournaments (name, participants) VALUES ('{name}', " + f'"{stringified_dict}");')
#         dbsession.commit()

# CALCULATE POINTS CODE
tournament_name = "Spicy_Mayo_Cup_7" # NEEDS A VALUE
query = dbsession.exec_driver_sql(f"SELECT name, participants FROM tournaments where name= '{tournament_name}';")
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


# SET BACK TO ZERO CODE
# dbsession.exec_driver_sql("UPDATE participants set total_points = 0;")
# dbsession.commit()
