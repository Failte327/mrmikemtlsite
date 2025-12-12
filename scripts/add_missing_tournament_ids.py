import requests
import sqlalchemy
from creds import api_key

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

tournaments_request = requests.get("https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments.json?state=ended", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})

tournament_data = tournaments_request.json()["data"]

existing_tournaments = dbsession.exec_driver_sql(f"SELECT name FROM tournaments WHERE tournament_id IS NULL;").all()

tournament_names = []

for tourney in existing_tournaments:
    tournament_names.append(tourney.name)

for tournament in tournament_data:
    name = tournament["attributes"]["name"].replace(" ", "_")
    id = tournament["id"]
    
    for i in tournament_names:
        if i == name:
            dbsession.exec_driver_sql(f"UPDATE tournaments SET tournament_id = {id} WHERE name = '{name}';")
            dbsession.commit()