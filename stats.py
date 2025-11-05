import requests

league = 0

human = 0
orc = 0
nightelf = 0
undead = 0

while league <= 21:
    print(f"Getting data for league {league+1}")
    response = requests.get(f"https://website-backend.w3champions.com/api/ladder/{league}?gateWay=20&gameMode=1&season=23")
    data = response.json()

    for player in data:
        if player.get("race") == 1:
            human = human + 1
        elif player.get("race") == 2:
            orc = orc + 1
        elif player.get("race") == 4:
            nightelf = nightelf + 1
        elif player.get("race") == 8:
            undead = undead + 1

    league = league + 1

print("STATS: ")
print(f"human: {human}")
print(f"orc: {orc}")
print(f"nightelf: {nightelf}")
print(f"undead: {undead}")