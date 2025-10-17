#attempting to have studybuddy.db is created automatically
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#this is going to represent a study session:
class Session(db.Model):
    id = db.Column(db.integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    location = db.Column(db.String(200), nullable=False)
    session_time = db.Column(db.DateTime, default=datetime.utc)