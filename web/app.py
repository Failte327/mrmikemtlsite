from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
import json
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'jelly-castle-before'
engine = sqlalchemy.create_engine("sqlite:///mrmikemtlsite/smf_tournaments_database.sqlite3")
dbsession = engine.connect()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Tells @login_required where to redirect guests

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    # Fetch user from DB to populate current_user
    result = dbsession.execute(
        sqlalchemy.text("SELECT id, username FROM users WHERE id = :id"),
        {"id": user_id}
    ).mappings().one_or_none()
    
    if result:
        return User(id=result['id'], username=result['username'])
    return None

@app.route("/")
@app.route("/index")
def index():
    upcoming_tournaments = []
    try:
        with open("mrmikemtlsite/upcoming_tournaments.txt", "r") as upcoming_file:
            lines = upcoming_file.readlines()
            for i in lines:
                if i.strip() != "":
                    new_list = i.split("|")
                    tournament = []
                    string_1 = new_list[0] + "| "
                    string_2 = new_list[1]
                    string_3_list = new_list[2].split("https://")
                    string_3 = string_3_list[0]
                    string_4 = string_3_list[1] if len(string_3_list) > 1 else ""
                    tournament.extend([string_1, string_2, string_3, string_4])
                    upcoming_tournaments.append(tournament)
    except FileNotFoundError:
        pass
        
    while len(upcoming_tournaments) < 3:
        upcoming_tournaments.append(["", "", "", ""])
    
    # Fetch latest 5 posts
    posts = dbsession.execute(sqlalchemy.text("SELECT * FROM posts ORDER BY date DESC LIMIT 5")).all()

    return render_template("index.html", upcoming_tournaments=upcoming_tournaments, posts=posts)

@app.route("/leaderboard")
def leaderboard():
    raw_data = dbsession.exec_driver_sql("SELECT name, total_points, user_id from participants2026 ORDER BY total_points desc;").all()
    data = []
    page_size = 30
    total = len(raw_data)
    total_pages = max(1, round(total / page_size))
    page = request.args.get("page", type=int) or 1
    
    starting_spot = (page - 1) * page_size + 1
    
    i = 1
    for record in raw_data:
        if i >= starting_spot and len(data) < page_size:
            if record is not None:
                if record.user_id is not None:
                    db_data_1 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM tournament_matches2026 WHERE participant_1_id = {record.user_id};").all()
                    db_data_2 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM tournament_matches2026 WHERE participant_2_id = {record.user_id};").all()
                    wins, losses = 0, 0
                    for w in db_data_1:
                        wins += w.participant_1_points
                        losses += w.participant_2_points
                    for n in db_data_2:
                        wins += n.participant_2_points
                        losses += n.participant_1_points
                    
                    data.append({
                        "rank": i,
                        "name": record.name,
                        "total_points": record.total_points,
                        "record": f"{wins} - {losses}"
                    })
                else:
                    data.append({
                        "rank": i,
                        "name": record.name,
                        "total_points": record.total_points,
                        "record": "Unknown"
                    })
        i += 1
    
    pages = list(range(1, total_pages + 1))
    return render_template("leaderboard.html", data=data, pages=pages)

@app.route("/events")
def events():
    data2025 = dbsession.exec_driver_sql("SELECT name FROM tournaments;").all()
    data2026 = dbsession.exec_driver_sql("SELECT name FROM tournaments2026;").all()
    all_events = data2025 + data2026

    event = request.args.get("event")
    if not event:
        raw_data = sorted(all_events)
        data = []
        page_size = 15
        total = len(raw_data)
        total_pages = max(1, round(total / page_size))
        page = request.args.get("page", type=int) or 1
        
        starting_spot = (page - 1) * page_size + 1
        i = 1
        for record in raw_data:
            if i >= starting_spot and len(data) < page_size:
                data.append({"name": record.name})
            i += 1
        
        pages = list(range(1, total_pages + 1))
        return render_template("events.html", data=data, pages=pages)
    else:
        is_2026 = False
        query1 = dbsession.exec_driver_sql(f"SELECT participants FROM tournaments WHERE name = '{event}';").one_or_none()
        if query1 is None:
            query = dbsession.exec_driver_sql(f"SELECT participants FROM tournaments2026 WHERE name = '{event}';").one_or_none()
            is_2026 = True
        else:
            query = query1
            
        if not query:
            return redirect(url_for('events'))

        tournament_data = eval(json.loads(json.dumps(query[0])))
        # Clean data
        tournament_data = {k: v for k, v in tournament_data.items() if v is not None}
        tournament_data = dict(sorted(tournament_data.items(), key=lambda item: item[1]))
        
        final_data = []
        for name, rank in tournament_data.items():
            q = dbsession.exec_driver_sql(f"SELECT user_id FROM participants WHERE name = '{name}';").one_or_none()
            if q and q[0]:
                user_id = q[0]
                table = "tournament_matches2026" if is_2026 else "tournament_matches"
                event_table = "tournaments2026" if is_2026 else "tournaments"
                
                event_id = dbsession.exec_driver_sql(f"SELECT tournament_id FROM {event_table} WHERE name = '{event}';").one()[0]
                
                db_data_1 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM {table} WHERE participant_1_id = {user_id} AND tournament_id = {event_id};").all()
                db_data_2 = dbsession.exec_driver_sql(f"SELECT participant_1_points, participant_2_points FROM {table} WHERE participant_2_id = {user_id} AND tournament_id = {event_id};").all()
                
                wins, losses = 0, 0
                for r in db_data_1:
                    wins += r.participant_1_points
                    losses += r.participant_2_points
                for r in db_data_2:
                    wins += r.participant_2_points
                    losses += r.participant_1_points
                
                final_data.append({"rank": rank, "name": name, "record": f"{max(0, wins)} - {max(0, losses)}"})
            else:
                final_data.append({"rank": rank, "name": name, "record": "Unknown"})
        
        return render_template("events.html", tournament_data=final_data)
    

@app.route("/news")
def news():
    posts = dbsession.execute(sqlalchemy.text("SELECT * FROM posts ORDER BY date;")).all()

    news_post = request.args.get("post")
    if not news_post:
        return render_template("news.html", posts=posts)
    else:
        for post in posts:
            if news_post == post.title:
                return render_template("news.html", news_post=post)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        existing_email = dbsession.execute(
            sqlalchemy.text("SELECT email FROM users WHERE email = :email"), 
            {"email": email}
        ).one_or_none()
        
        existing_user = dbsession.execute(
            sqlalchemy.text("SELECT username FROM users WHERE username = :username"), 
            {"username": username}
        ).one_or_none()

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('signup'))
        
        if existing_email:
            flash("Email already exists!")
            return redirect(url_for('signup'))
        
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Secure Insert
        dbsession.execute(
            sqlalchemy.text("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)"),
            {"username": username, "email": email, "password": hashed_pw}
        )
        dbsession.commit()
        
        flash("Account created! Please login.")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        result = dbsession.execute(
            sqlalchemy.text(f"SELECT id, username, password FROM users WHERE email = '{email}';"),
            {"email": email}
        ).mappings().one_or_none()

        if result and check_password_hash(result['password'], password):
            user_obj = User(id=result['id'], username=result['username'])
            
            login_user(user_obj) 
            
            flash(f"Login successful! Welcome {user_obj.username}")
            return redirect(url_for('index'))
        
        flash("Invalid email or password.")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user() # Clears the session and cookie automatically
    flash("You have been logged out.")
    return redirect(url_for('index'))

@app.route("/point_system")
def point_system():
    return render_template("points_breakdown.html")

@app.route("/upcoming")
def upcoming():
    upcoming_tournaments = []
    try:
        with open("mrmikemtlsite/upcoming_tournaments.txt", "r") as upcoming_file:
            lines = upcoming_file.readlines()
            for i in lines:
                if i.strip() != "":
                    parts = i.split("|")
                    if len(parts) >= 3:
                        s3 = parts[2].split("https://")
                        upcoming_tournaments.append([parts[0] + "| ", parts[1], s3[0], s3[1] if len(s3)>1 else ""])
    except FileNotFoundError:
        pass
    return render_template("upcoming.html", upcoming_tournaments=upcoming_tournaments)

@app.route("/smf_league")
def smf_league():
    return render_template("smf_league.html")

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    # Only allow admins to post
    if not current_user.is_authenticated or current_user.username not in ['reklewt', 'mrmikemtl']:
        flash("You do not have permission to access this page.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = current_user.username

        dbsession.execute(
            sqlalchemy.text("INSERT INTO posts (title, content, author) VALUES (:title, :content, :author)"),
            {"title": title, "content": content, "author": author}
        )
        dbsession.commit()
        flash("Post created successfully!")
        return redirect(url_for('index'))

    return render_template('create_post.html')

if __name__ == '__main__':
    app.run()