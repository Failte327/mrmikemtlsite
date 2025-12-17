from creds import api_key
import sqlalchemy
import requests

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

ids = []

existing_tournaments = dbsession.exec_driver_sql(f"SELECT tournament_id FROM tournaments;").all()

for tourney in existing_tournaments:
    ids.append(tourney.tournament_id)

tournaments_with_no_matches = []

for id in ids:
    matches_query = dbsession.exec_driver_sql(f"SELECT tournament_id FROM tournament_matches WHERE tournament_id = '{id}';").all()
    if len(matches_query) == 0:
        participant_ids_to_user_ids = {}
        participants_request = requests.get(f"https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments/{id}/participants.json", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        participants_data = participants_request.json()["data"]
        for participant in participants_data:
            if participant is not None:
                if participant.get("relationships") is not None:
                    if participant.get("relationships").get("user") is not None:
                        user_id = participant.get("relationships").get("user").get("data").get("id")
                        if user_id not in participant_ids_to_user_ids.values():
                            participant_ids_to_user_ids[participant.get("id")] = user_id

        matches_request = requests.get(f"https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments/{id}/matches.json", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        match_data = matches_request.json()["data"]

        for match in match_data:
            if match is not None:
                participant_1 = str(match.get("attributes").get("points_by_participant")[0].get("participant_id"))
                participant_2 = str(match.get("attributes").get("points_by_participant")[1].get("participant_id"))
                if participant_1 in participant_ids_to_user_ids:
                    participant_1_user_id = int(participant_ids_to_user_ids[participant_1])
                else:
                    participant_1_user_id = 0
                if participant_2 in participant_ids_to_user_ids:
                    participant_2_user_id = int(participant_ids_to_user_ids[participant_2])
                else:
                    participant_2_user_id = 0
                participant_1_points = int(match.get("attributes").get("scores").split(" - ")[0])
                participant_2_points = int(match.get("attributes").get("scores").split(" - ")[1])
                dbsession.exec_driver_sql(f"INSERT INTO tournament_matches (participant_1_id, participant_2_id, participant_1_points, participant_2_points, tournament_id) VALUES ({participant_1_user_id}, {participant_2_user_id}, {participant_1_points}, {participant_2_points}, {id});")
                dbsession.commit()
                print(f"Added match between {participant_1_user_id} and {participant_2_user_id}, score was {participant_1_points} - {participant_2_points}. Played in tournament {id}")




# for username, user_id in names_to_ids.items():
#     query = dbsession.exec_driver_sql(f"SELECT name, user_id FROM participants where name= '{username}';").all()
#     if len(query) > 0:
#         if query[0].user_id is None:
#             dbsession.exec_driver_sql(f"UPDATE participants SET user_id = {user_id} WHERE name = '{username}';")
#             dbsession.commit()
#             print(f"updated {username}'s user_id record to {user_id}")