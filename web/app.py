from flask import Flask, render_template, request
import sqlalchemy
import json

app = Flask(__name__)

dbsession = sqlalchemy.create_engine("sqlite:///mrmikemtlsite/smf_tournaments_database.sqlite3").connect()

@app.route("/")
@app.route("/index")
def index():
	upcoming_tournaments = []
	with open("mrmikemtlsite/upcoming_tournaments.txt", "r") as upcoming_file:
		list = upcoming_file.readlines()
		for i in list:
			if i != "":
				new_list = i.split("|")
				tournament = []
				string_1 = new_list[0] + "| "
				string_2 = new_list[1]
				string_3_list = new_list[2].split("https://")
				string_3 = string_3_list[0]
				string_4 = string_3_list[1]
				tournament.append(string_1)
				tournament.append(string_2)
				tournament.append(string_3)
				tournament.append(string_4)
				upcoming_tournaments.append(tournament)
		
		while len(upcoming_tournaments) < 3:
			upcoming_tournaments.append(["", "", "", ""])

	return render_template("index.html", upcoming_tournaments=upcoming_tournaments)

@app.route("/leaderboard")
def leaderboard():
	raw_data = dbsession.exec_driver_sql("SELECT name, total_points, user_id from participants2026 ORDER BY total_points desc;").all()
	data = []
	page_size = 30
	total = len(raw_data)
	total_pages = round(total / page_size)
	page = request.args.get("page")
	if page is not None:
		page = int(page)
	if page is None:
		starting_spot = 1
	elif page == 1:
		starting_spot = 1
	else:
		starting_spot = (page - 1) * page_size + 1
	i = 1
	for record in raw_data:
		if i >= starting_spot and len(data) < page_size:
			if record is not None:
				if record.user_id is not None:
					db_data_1 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM tournament_matches2026 WHERE participant_1_id = {record.user_id};").all()
					db_data_2 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM tournament_matches2026 WHERE participant_2_id = {record.user_id};").all()
					wins = 0
					losses = 0
					for w in db_data_1:
						wins = wins + w.participant_1_points
						losses = losses + w.participant_2_points
					for n in db_data_2:
						wins = wins + n.participant_2_points
						losses = losses + n.participant_1_points
					data_obj = {
						"rank": i,
						"name": record.name,
						"total_points": record.total_points,
						"record": f"{wins} - {losses}"
					}
					data.append(data_obj)
				else:
					data_obj = {
						"rank": i,
						"name": record.name,
						"total_points": record.total_points,
						"record": f"Unknown"
					}
					data.append(data_obj)
			else:
				data_obj = {
						"rank": i,
						"name": record.name,
						"total_points": record.total_points,
						"record": f"Unknown"
				}
				data.append(data_obj)
		i = i + 1
	
	pages = []
	page_num = 1
	while len(pages) < total_pages:
		pages.append(page_num)
		page_num = page_num + 1

	return render_template("leaderboard.html", data=data, pages=pages)

@app.route("/events")
def events():
	data = dbsession.exec_driver_sql("SELECT name FROM tournaments;").all()

	event = request.args.get("event")
	if not event:
		raw_data = sorted(data)
		data = []
		page_size = 15
		total = len(raw_data)
		total_pages = round(total / page_size)
		page = request.args.get("page")
		if page is not None:
			page = int(page)
		if page is None:
			starting_spot = 1
		elif page == 1:
			starting_spot = 1
		else:
			starting_spot = (page - 1) * page_size + 1
		i = 1
		for record in raw_data:
			if i >= starting_spot and len(data) < page_size:
				data_obj = {
					"name": record.name,
				}
				data.append(data_obj)
			i = i + 1
		
		pages = []
		page_num = 1
		while len(pages) < total_pages:
			pages.append(page_num)
			page_num = page_num + 1

		return render_template("events.html", data=data, pages=pages)
	else:
		query = dbsession.exec_driver_sql(f"SELECT participants FROM tournaments WHERE name = '{event}';").one()
		raw_data = json.dumps(query[0])
		tournament_data = eval(json.loads(raw_data))
		non_placers = []
		for key, val in tournament_data.items():
			if val is None:
				non_placers.append(key)
		
		for i in non_placers:
			del tournament_data[i]
		tournament_data = dict(sorted(tournament_data.items(), key=lambda item: item[1]))
		data = []
		for name, rank in tournament_data.items():
			q = dbsession.exec_driver_sql(f"SELECT user_id FROM participants WHERE name = '{name}';").one_or_none()
			if q is not None:
				if q[0] is not None:
					user_id = q[0]
					event_id = dbsession.exec_driver_sql(f"SELECT tournament_id FROM tournaments WHERE name = '{event}';").one()[0]
					db_data_1 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM tournament_matches WHERE participant_1_id = {user_id} AND tournament_id = {event_id};").all()
					db_data_2 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM tournament_matches WHERE participant_2_id = {user_id} AND tournament_id = {event_id};").all()
					wins = 0
					losses = 0
					for i in db_data_1:
						wins = wins + i.participant_1_points
						losses = losses + i.participant_2_points
					for n in db_data_2:
						wins = wins + n.participant_2_points
						losses = losses + n.participant_1_points
					if losses < 0:
						losses = 0
					display_obj = {
						"rank": rank,
						"name": name,
						"record": f"{wins} - {losses}"
					}
					data.append(display_obj)
				else:
					display_obj = {
					"rank": rank,
					"name": name,
					"record": f"Unknown"
					}
					data.append(display_obj)
			else:
				display_obj = {
					"rank": rank,
					"name": name,
					"record": f"Unknown"
				}
				data.append(display_obj)
		
		return render_template("events.html", tournament_data=data)
	
@app.route("/login")
def login():
	# LOGIN NOT IMPLEMENTED YET
	return render_template("login.html")

@app.route("/point_system")
def point_system():
	return render_template("points_breakdown.html")

@app.route("/upcoming")
def upcoming():
	upcoming_tournaments = []
	with open("mrmikemtlsite/upcoming_tournaments.txt", "r") as upcoming_file:
		list = upcoming_file.readlines()
		for i in list:
			if i != "":
				new_list = i.split("|")
				tournament = []
				string_1 = new_list[0] + "| "
				string_2 = new_list[1]
				string_3_list = new_list[2].split("https://")
				string_3 = string_3_list[0]
				string_4 = string_3_list[1]
				tournament.append(string_1)
				tournament.append(string_2)
				tournament.append(string_3)
				tournament.append(string_4)
				upcoming_tournaments.append(tournament)

	return render_template("upcoming.html", upcoming_tournaments=upcoming_tournaments)

@app.route("/smf_league")
def smf_league():
	return render_template("smf_league.html")

if __name__ == '__main__':
	app.run()
