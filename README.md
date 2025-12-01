# COMPILING CSS -- necessary when changes are made to the classes inside the HTML (add, subtract, etc)

npx @tailwindcss/cli -i ./static/src/input.css -o ./static/dist/output.css --watch

# RUNNING IN DEBUG MODE

flask run

# Updating leaderboard point totals

cd into scripts/ and run ./update_points.sh