from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from datetime import datetime, timezone
from models import db, Session

#This file is used to create and run the website
#, connecting everything together. 
app = Flask(__name__)
#app.config.from_object(Config) <-meant to load settings from config file

#fixed the typo, supposedly "URI" instead of URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#db = SQLAlchemy() commented this out since I imported from models.py

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #the name of the login route

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String(200), nullable=False)#description of task
    date_created = db.Column(db.DateTime, default=datetime.utc)#automatically saves date and time


@app.route('/')
def home():
    sessions = Session.query.all()
    return render_template('index.html', sessions=sessions)

with app.app_context():
    db.create_all() #to my understanding this is incase if no database is found. 

if __name__ == '__main__':
    app.run(debug=True)