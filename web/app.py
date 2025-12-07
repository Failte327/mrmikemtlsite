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
	raw_data = dbsession.exec_driver_sql("SELECT name, total_points from participants ORDER BY total_points desc;").all()
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
			data_obj = {
				"rank": i,
				"name": record.name,
				"total_points": record.total_points
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
		
		return render_template("events.html", tournament_data=tournament_data)
	
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

if __name__ == '__main__':
	app.run()
