# ====== IMPORTS & APP CONFIG ======
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = 'superdupermegaexclusivesecretkeyshh'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ====== DATABASE MODELS ======
session_attendees = db.Table(
    'session_attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user_profile.id')),
    db.Column('session_id', db.Integer, db.ForeignKey('study_session.id'))
)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    major = db.Column(db.String(80), default="")
    bio = db.Column(db.Text, default="")
    classes = db.Column(db.Text, default="")
    interests = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    sessions_created = db.relationship("StudySession", backref="creator", lazy=True)


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
        secondary=session_attendees,
        backref='joined_sessions'
    )


# ====== MAIN & LOGIN ======
@app.route('/')
def home():
    #re-route to login page
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('session_page'))

    if request.method == 'POST':
        try:
            #ensures institution email being used
            user_email = request.form['user']
            local_part, institution = user_email.split('@')
            first_name = local_part.split('.')[0].capitalize()
        except:
            return render_template('login.html')

        if institution != 'utrgv.edu':
            return render_template('login.html')

        #checks to see if profile exists
        profile = UserProfile.query.filter_by(name=first_name).first()
        if not profile:
            profile = UserProfile(name=first_name)
            db.session.add(profile)
            db.session.commit()

        session['user'] = first_name
        return redirect(url_for('session_page'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ====== SESSION ROUTES ======
@app.route('/sessions')
def session_page():
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    current_user = UserProfile.query.filter_by(name=username).first()
    all_sessions = StudySession.query.all()

    # Created OR joined
    my_sessions = [
        s for s in all_sessions
        if s.creator_id == current_user.id or current_user in s.attendees
    ]

    upcoming = my_sessions  # for now

    return render_template(
        'session.html',
        sessions=all_sessions,
        my_sessions=my_sessions,
        upcoming=upcoming,
        current_user=current_user   # ✅ ADD THIS
    )



@app.route('/profile/<usr>/create-session', methods=['GET', 'POST'])
def create_session(usr):
    profile = UserProfile.query.filter_by(name=usr).first_or_404()

    if request.method == 'POST':
        sess = StudySession(
            creator_id=profile.id,
            title=request.form['title'],
            subject=request.form['subject'],
            description=request.form['description'],
            location=request.form['location'],
            date_time=request.form['date_time'],
            is_public='is_public' in request.form
        )
        db.session.add(sess)
        db.session.commit()
        return redirect(url_for('session_page'))

    return render_template('create_session.html', profile=profile)

@app.route('/session/<int:session_id>')
def session_detail(session_id):
    sess = StudySession.query.get_or_404(session_id)
    creator = UserProfile.query.get(sess.creator_id)

    current_user = None
    if session.get('user'):
        current_user = UserProfile.query.filter_by(
            name=session.get('user')
        ).first()

    return render_template(
        'session_detail.html',
        study_session=sess,
        creator=creator,
        current_user=current_user
    )


@app.route('/join-session/<int:session_id>', methods=['POST'])
def join_session(session_id):
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    user = UserProfile.query.filter_by(name=username).first()
    sess = StudySession.query.get_or_404(session_id)

    # Creator cannot join their own session
    if sess.creator_id == user.id:
        return redirect(url_for('session_detail', session_id=session_id))

    # Prevent duplicate joins
    if user not in sess.attendees:
        sess.attendees.append(user)
        db.session.commit()

    return redirect(url_for('session_detail', session_id=session_id))


@app.route('/delete-session/<int:session_id>', methods=['POST'])
def delete_session(session_id):
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    user = UserProfile.query.filter_by(name=username).first()
    sess = StudySession.query.get_or_404(session_id)

    if sess.creator_id != user.id:
        return redirect(url_for('session_page'))

    db.session.delete(sess)
    db.session.commit()

    return redirect(url_for('session_page'))

@app.route('/edit-session/<int:session_id>', methods=['GET', 'POST'])
def edit_session(session_id):
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    user = UserProfile.query.filter_by(name=username).first()
    sess = StudySession.query.get_or_404(session_id)

    if sess.creator_id != user.id:
        return redirect(url_for('session_page'))

    if request.method == 'POST':
        sess.title = request.form['title']
        sess.subject = request.form['subject']
        sess.description = request.form['description']
        sess.location = request.form['location']
        sess.date_time = request.form['date_time']
        sess.is_public = 'is_public' in request.form
        db.session.commit()
        return redirect(url_for('session_detail', session_id=session_id))

    return render_template('edit_session.html', study_session=sess)



# ====== PROFILE ROUTES ======
@app.route('/profile/<usr>')
def user(usr):
    profile = UserProfile.query.filter_by(name=usr).first_or_404()

    created_sessions = StudySession.query.filter_by(
        creator_id=profile.id
    ).all()

    joined_sessions = profile.joined_sessions

    # Combine + remove duplicates
    sessions = list(set(created_sessions + joined_sessions))

    return render_template(
        'user.html',
        profile=profile,
        sessions=sessions
    )


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


# ====== CALENDER  ======
@app.route('/calendar')
def calendar():
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    user = UserProfile.query.filter_by(name=username).first()
    all_sessions = StudySession.query.all()

    calendar_events = {}   # All events grouped by date
    my_events = {}         # User's events grouped by date

    for s in all_sessions:
        date_key = s.date_time.split()[0] if s.date_time else "Unscheduled"

        # ---- All events (calendar view) ----
        calendar_events.setdefault(date_key, []).append(s)

        # ---- My Calendar (created OR joined) ----
        if s.creator_id == user.id or user in s.attendees:
            my_events.setdefault(date_key, []).append(s)

    return render_template(
        'calendar.html',
        calendar_events=calendar_events,
        my_events=my_events
    )



# ====== RUN APP ======
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
