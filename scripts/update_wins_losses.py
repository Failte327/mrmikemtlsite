from creds import api_key
import sqlalchemy
import requests

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

ids = []

existing_tournaments = dbsession.exec_driver_sql(f"SELECT name FROM tournaments;").all()

for tourney in existing_tournaments:
    split = tourney.name.split("-")
    if len(split) > 1:
        ids.append(split[1])

for id in ids:
    matches_request = requests.get(f"https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments/{id}/matches.json", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
    participants_data = matches_request.json()["data"]

    for participant in participants_data:
        if participant is not None:
            attributes = participant.get("attributes")
            print(participant)
    # dbsession.exec_driver_sql(f"INSERT INTO tournaments (name, participants) VALUES ('{name}', " + f'"{stringified_dict}");')
    # dbsession.commit()