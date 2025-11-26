from flask import Flask, render_template, request, redirect, url_for, session
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
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        local_part,institution = user.split('@')
        name_part = local_part.split('.')
        first_name = name_part[0]

        if institution != 'utrgv.edu':
            return render_template('login.html')

        return redirect(url_for("user", usr = first_name.capitalize()))
    else:
        return render_template('login.html')


@app.route('/')
def home():
    #current_user = {'name': 'user'}
    current_user = 'user'
    return render_template('home.html',user = current_user)

@app.route('/session')
def session_page():
    sessions = Post.query.all()
    return render_template('session.html', sessions=sessions)
    #pass
    #to my understanding this is incase if no database is found.
    # N: Had to fix the name of the route function.  

@app.route('/<usr>')
def user(usr):
    return render_template('user.html',user_name=usr)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)