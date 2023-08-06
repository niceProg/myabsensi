import os
from flask import Flask, render_template, url_for, session, redirect, flash, request
from dotenv import load_dotenv

load_dotenv()  # read env file
app = Flask(__name__)  # init flask app

# konfigurasi variabel global flask
app.config["BASE_URL"] = os.getenv("BASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["attendance_detected"] = False

# import blueprint
from routes.dashboard import Dashboard
from routes.auth import Auth
from routes.absensi import Absensi

# register blueprint
app.register_blueprint(Dashboard)
app.register_blueprint(Auth)
app.register_blueprint(Absensi)


# root routing
@app.route("/")
def home():
    return render_template(
        title="Home Page | My Absensi", template_name_or_list="home/home.html"
    )


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT"))
