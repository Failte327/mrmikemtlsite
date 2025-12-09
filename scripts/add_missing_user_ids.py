from creds import api_key
import sqlalchemy
import requests

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

tournaments_request = requests.get("https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments.json?state=ended", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})

tournament_data = tournaments_request.json()["data"]

existing_tournaments = dbsession.exec_driver_sql(f"SELECT name FROM tournaments;").all()

tournament_names = []

for tourney in existing_tournaments:
    tournament_names.append(tourney.name)

for tournament in tournament_data:
    name = tournament["attributes"]["name"].replace(" ", "_")
    id = tournament["id"]

    participants = {}
    participants_request = requests.get(f"https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments/{id}/participants.json", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
    participants_data = participants_request.json()["data"]

    for participant in participants_data:
        name = participant.get("attributes").get("username")
        if participant.get("relationships") is not None:
            if participant.get("relationships").get("user") is not None:
                user_id = participant.get("relationships").get("user").get("data").get("id")
                query = dbsession.exec_driver_sql(f"SELECT name, user_id FROM participants WHERE name = '{name}';").all()
                if len(query) == 0:
                    dbsession.exec_driver_sql(f"INSERT INTO participants (name, total_points, user_id) VALUES ('{name}', 0, {user_id});")
                    dbsession.commit()
                    print(f"Added participant {name} with user_id {user_id} to the database.")