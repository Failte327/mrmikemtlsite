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
    tournament_full_name = f"{name}-{id}"

    # Check to see if we already have the data
    if tournament_full_name not in tournament_names:
        if name not in tournament_names:
            print(f"Gathering data for {tournament_full_name}...")
            participants = {}
            participants_request = requests.get(f"https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments/{id}/participants.json", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
            participants_data = participants_request.json()["data"]

            for participant in participants_data:
                if participant is not None:
                    attributes = participant.get("attributes")
                    if participant.get("relationships").get("user"):
                        participant_id = participant.get("relationships").get("user").get("id")
                        username = attributes.get("username")
                        placement = attributes.get("final_rank")
                        participants[username] = placement

            stringified_dict = str(participants)
            dbsession.exec_driver_sql(f"INSERT INTO tournaments (name, participants) VALUES ('{name}', " + f'"{stringified_dict}");')
            dbsession.commit()

# Update upcoming_tournaments.txt
upcoming_tournaments_request = requests.get("https://api.challonge.com/v2.1/communities/showmatchfriday/tournaments.json?state=pending", headers={"Authorization-Type": "v1", "Authorization": api_key, "Content-Type": "application/vnd.api+json", "Accept": "application/json", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
upcoming_tournaments_data = upcoming_tournaments_request.json()["data"]

tournaments_to_timestamp_map = {}
tournaments_to_link_map = {}
for upcoming in upcoming_tournaments_data:
    name = upcoming["attributes"]["name"]
    date = upcoming["attributes"]["timestamps"]["starts_at"].split("T")[0]
    tournaments_to_timestamp_map[name] = date

for upcoming in upcoming_tournaments_data:
    name = upcoming["attributes"]["name"]
    link = upcoming["attributes"]["full_challonge_url"]
    tournaments_to_link_map[name] = link

with open("../upcoming_tournaments.txt", "w") as file:
    for name1, date in tournaments_to_timestamp_map.items():
        for name2, link in tournaments_to_link_map.items():
            if name1 == name2:
                file.write(f"{name1} | {date} | Sign up here: {link}\n")
