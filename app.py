from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataman.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user'] = username
            return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/answer_checker', methods=['GET', 'POST'])
def answer_checker():
    difficulty = request.args.get('difficulty') or session.get('difficulty', 'easy')
    session['difficulty'] = difficulty

    feedback = None
    feedback_class = None

    if 'score' not in session:
        session['score'] = 0
        session['count'] = 0
        session['streak'] = 0

    if request.method == 'POST':
        user_answer = request.form['answer'] == 'true'
        correct = session.get('correct', False)

        if user_answer == correct:
            session['score'] += 1
            session['streak'] += 1
            feedback = "Correct!"
            feedback_class = "correct"
        else:
            session['streak'] = 0
            feedback = "Incorrect. Try the next one!"
            feedback_class = "incorrect"

        session['count'] += 1

        if session['count'] >= 15:
            score = session['score']
            total = session['count']
            accuracy = int((score / total) * 100)

            result = GameResult(
                username=session.get('user', 'Guest'),
                score=score,
                total=total,
                accuracy=accuracy,
                difficulty=session.get('difficulty', 'easy')
            )

            db.session.add(result)
            db.session.commit()

            session.clear()

            return render_template(
                'game_over.html',
                score=score,
                total=total,
                accuracy=accuracy
            )

    if difficulty == 'easy':
        max_num = 10
    elif difficulty == 'medium':
        max_num = 20
    else:
        max_num = 50

    a = random.randint(1, max_num)
    b = random.randint(1, max_num)

    operation = random.choice(['+', '-', '*'])

    if operation == '+':
        correct = a + b
    elif operation == '-':
        correct = a - b
    else:
        correct = a * b

    if random.choice([True, False]):
        shown = correct
    else:
        shown = correct + random.randint(-3, 3)

    session['correct'] = (shown == correct)

    return render_template(
        'answer_checker.html',
        question=f"{a} {operation} {b} = {shown}",
        score=session['score'],
        count=session['count'],
        streak=session['streak'],
        difficulty=difficulty,
        feedback=feedback,
        feedback_class=feedback_class
    )

@app.route('/number_guesser', methods=['GET', 'POST'])
def number_guesser():
    message = None

    if 'secret_number' not in session:
        session['secret_number'] = random.randint(1, 20)
        session['guess_count'] = 0

    if request.method == 'POST':
        guess = int(request.form['guess'])
        session['guess_count'] += 1

        if guess < session['secret_number']:
            message = "Too low!"
        elif guess > session['secret_number']:
            message = "Too high!"
        else:
            attempts = session['guess_count']
            session.pop('secret_number', None)
            session.pop('guess_count', None)
            return render_template('number_guesser.html', message=f"Correct! You guessed it in {attempts} attempts.", game_over=True)

    return render_template(
        'number_guesser.html',
        message=message,
        guess_count=session['guess_count'],
        game_over=False
    )

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)