import sqlalchemy

dbsession = sqlalchemy.create_engine("sqlite:///../smf_tournaments_database.sqlite3").connect()

# SET BACK TO ZERO CODE
dbsession.exec_driver_sql("UPDATE participants2026 set total_points = 0;")
dbsession.commit()