from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


#This file is used to create and run the website
#, connecting everything together. 
app = Flask(__name__)

#fixed the typo, supposedly "URI" instead of URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    


@app.route('/')
def home():
    return render_template('home.html',user = 'user')


@app.route('/<name>')
def user(name):
    return f'Hello  {name}!'


@app.route('/sessions')
def sessions():
    sessions = Post.query.all()
    return render_template('index.html')
    #pass
    #to my understanding this is incase if no database is found. 


    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)