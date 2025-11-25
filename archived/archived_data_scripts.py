## CODE FOR PARSING TOURNAMENTS_DATA.JSON
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

# files = os.listdir("finished_tournaments/")

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