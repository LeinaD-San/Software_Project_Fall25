from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


app = Flask(__name__)
app.secret_key = 'superdupermegaexclusivesecretkeyshh'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
'Tamara here now:)'

# -----------------------------
# DATABASE MODELS
# -----------------------------
friendship = db.Table('friendship',
    db.Column('user_id', db.Integer, db.ForeignKey('user_profile.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user_profile.id'))
    
    )

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    major = db.Column(db.String(80), default="")
    bio = db.Column(db.Text, default="")
    classes = db.Column(db.Text, default="")
    interests = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    posts = db.relationship("UserPost", backref="profile", lazy=True)
    sessions_created = db.relationship("StudySession", backref="creator", lazy=True)

    friends = db.relationship(
    'UserProfile',
    secondary='friendship',
    primaryjoin=(id == friendship.c.user_id),
    secondaryjoin=(id == friendship.c.friend_id),
    backref='friend_of'
)



class UserPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    to_user = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    status = db.Column(db.String(20), default="pending")  # pending, accepted, denied



session_attendees = db.Table('session_attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user_profile.id')),
    db.Column('session_id', db.Integer, db.ForeignKey('study_session.id'))
)


class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(80))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    date_time = db.Column(db.String(50))
    is_public = db.Column(db.Boolean, default=True)

    attendees = db.relationship(
    'UserProfile',
    secondary='session_attendees',
    backref='joined_sessions'
)



# -----------------------------
# LOGIN
# -----------------------------
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            user_email = request.form['user']
            local_part, institution = user_email.split('@')

            if not local_part:
                raise ValueError('Invalid email')

            name_part = local_part.split('.')
            first_name = name_part[0].capitalize()

        except:
            return render_template('login.html')

        if institution != 'utrgv.edu':
            return render_template('login.html')

        # Create user profile if not exists
        profile = UserProfile.query.filter_by(name=first_name).first()

        if not profile:
            profile = UserProfile(name=first_name)
            db.session.add(profile)
            db.session.commit()

        # 🔥 Store login in Flask session
        session['user'] = first_name

        # Go to user dashboard
        return redirect(url_for('user', usr=first_name))

    return render_template('login.html')



# -----------------------------
# HOME
# -----------------------------
@app.route('/')
def home():
    current_user = session.get('user', None)
    return render_template('home.html', user=current_user)
'''
@app.route('/sessions')
def sessions_page():
    sessions = StudySession.query.all()
    return render_template('session.html', sessions=sessions)
'''

# -----------------------------
# CREATE STUDY SESSION
# -----------------------------
@app.route('/profile/<usr>/create-session', methods=['POST', 'GET'])
def create_session(usr):
    profile = UserProfile.query.filter_by(name=usr).first_or_404()

    if request.method == 'POST':
        session_obj = StudySession(
            creator_id=profile.id,
            title=request.form['title'],
            subject=request.form['subject'],
            description=request.form['description'],
            location=request.form['location'],
            date_time=request.form['date_time'],
            is_public=request.form.get('is_public') == 'on'
        )
        db.session.add(session_obj)
        db.session.commit()
        return redirect(url_for('user', usr=usr))

    return render_template('create_session.html', profile=profile)

'''
@app.route('/edit-session/<int:session_id>',methods=['GET','POST'])
def edit_session(session_id):
    sess = StudySession.query.get_or_404(session_id)

    if request.method == 'POST':
        sess.title = request.form['title']
        sess.subject = request.form['subject']
        sess.description = request.form['description']
        sess.location = request.form['location']
        sess.date_time = request.form['date_time']
        sess.is_public = request.form['is_public'] == 'on'

        db.session.commit()
        return redirect(url_for('session_page'))

    return render_template('edit_session.html',session=sess)


@app.route('/delete-session/<int:session_id',methods = ['POST'])
def delete_session(session_id):
    sess = StudySession.query.get_or_404(session_id)

    db.session.delete(sess)
    db.session.commit()

    return redirect(url_for('session_page'))
           
'''

# -----------------------------
# CREATE POST
# -----------------------------
@app.route('/profile/<usr>/new-post', methods=['GET', 'POST'])
def new_post(usr):
    profile = UserProfile.query.filter_by(name=usr).first_or_404()

    if request.method == 'POST':
        post = UserPost(
            user_id=profile.id,
            content=request.form['content']
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('user', usr=usr))

    return render_template('new_post.html', profile=profile)



@app.route('/profile/<usr>/edit', methods=['GET', 'POST'])
def edit_profile(usr):
    profile = UserProfile.query.filter_by(name=usr).first_or_404()

    if request.method == 'POST':
        profile.major = request.form.get('major', '')
        profile.classes = request.form.get('classes', '')
        profile.interests = request.form.get('interests', '')
        profile.bio = request.form.get('bio', '')
        db.session.commit()
        return redirect(url_for('user', usr=usr))

    return render_template('edit_profile.html', profile=profile)


def is_friend(user1, user2):
    return user2 in user1.friends

@app.route('/sessions')
def session_page():
    username = session.get('user')
    current_user = UserProfile.query.filter_by(name=username).first() if username else None

    all_sessions = StudySession.query.all()
    visible_sessions = []

    for s in all_sessions:
        if s.is_public:
            visible_sessions.append(s)
        else:
            # private: only friends of creator can view
            creator = s.creator
            if current_user and is_friend(current_user, creator):
                visible_sessions.append(s)

    return render_template('session.html', sessions=visible_sessions)

@app.route('/join-session/<int:session_id>', methods=['POST'])
def join_session(session_id):
    username = session.get('user')

    if not username:
        return redirect(url_for('login'))

    user = UserProfile.query.filter_by(name=username).first()
    sess = StudySession.query.get_or_404(session_id)

    # Check if already attending
    if user not in sess.attendees:
        sess.attendees.append(user)
        db.session.commit()

    return redirect(url_for('session_page'))

'''

'''





# -----------------------------
# USER PROFILE DASHBOARD
# -----------------------------
@app.route('/profile/<usr>')
def user(usr):
    profile = UserProfile.query.filter_by(name=usr).first_or_404()
    user_posts = UserPost.query.filter_by(user_id=profile.id).all()
    sessions = StudySession.query.filter_by(creator_id=profile.id).all()

    return render_template(
        'user.html',
        profile=profile,
        posts=user_posts,
        sessions=sessions
    )


@app.route('/profile/<usr>/send-friend-request', methods=['POST'])
def send_friend_request(usr):
    sender_name = session.get('user')
    sender = UserProfile.query.filter_by(name=sender_name).first()
    receiver = UserProfile.query.filter_by(name=usr).first()

    if sender and receiver and sender != receiver:
        req = FriendRequest(from_user=sender.id, to_user=receiver.id)
        db.session.add(req)
        db.session.commit()

    return redirect(url_for('user', usr=usr))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/feed")
def feed():
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    posts = UserPost.query.order_by(UserPost.created_at.desc()).all()
    return render_template("feed.html", posts=posts)


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
