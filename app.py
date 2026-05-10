from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import time

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

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    results = GameResult.query.filter_by(
        username=session['user']
    ).all()

    total_games = len(results)

    if total_games > 0:
        average_accuracy = round(
            sum(result.accuracy for result in results) / total_games,
            1
        )

        highest_score = max(result.score for result in results)
    else:
        average_accuracy = 0
        highest_score = 0

    return render_template(
        'dashboard.html',
        results=results,
        total_games=total_games,
        average_accuracy=average_accuracy,
        highest_score=highest_score
    )

@app.route('/speed_round', methods=['GET', 'POST'])
def speed_round():
    feedback = None
    feedback_class = None

    if 'speed_start_time' not in session:
        session['speed_start_time'] = time.time()
        session['speed_score'] = 0
        session['speed_count'] = 0

    elapsed = int(time.time() - session['speed_start_time'])
    time_left = max(0, 30 - elapsed)

    if time_left <= 0:
        return redirect(url_for('speed_round_game_over'))

    if request.method == 'POST':
        user_answer = int(request.form['answer'])
        correct_answer = session.get('speed_correct_answer')

        if user_answer == correct_answer:
            session['speed_score'] += 1
            feedback = "Correct!"
            feedback_class = "correct"
        else:
            feedback = f"Incorrect! Correct answer was {correct_answer}."
            feedback_class = "incorrect"

        session['speed_count'] += 1

    a = random.randint(1, 12)
    b = random.randint(1, 12)
    operation = random.choice(['+', '-', '*'])

    if operation == '+':
        correct_answer = a + b
    elif operation == '-':
        correct_answer = a - b
    else:
        correct_answer = a * b

    session['speed_correct_answer'] = correct_answer

    return render_template(
        'speed_round.html',
        question=f"{a} {operation} {b}",
        score=session['speed_score'],
        count=session['speed_count'],
        feedback=feedback,
        feedback_class=feedback_class,
        time_left=time_left
    )

@app.route('/speed_round_game_over')
def speed_round_game_over():
    score = session.get('speed_score', 0)
    total = session.get('speed_count', 0)

    session.pop('speed_score', None)
    session.pop('speed_count', None)
    session.pop('speed_correct_answer', None)
    session.pop('speed_start_time', None)

    return render_template(
        'speed_round_game_over.html',
        score=score,
        total=total
    )

@app.route('/fill_it_in', methods=['GET', 'POST'])
def fill_it_in():
    feedback = None
    feedback_class = None

    if 'fill_score' not in session:
        session['fill_score'] = 0
        session['fill_count'] = 0

    if request.method == 'POST':
        user_answer = int(request.form['answer'])
        correct_answer = session.get('fill_correct_answer')

        if user_answer == correct_answer:
            session['fill_score'] += 1
            feedback = "Correct!"
            feedback_class = "correct"
        else:
            feedback = f"Incorrect! Correct answer was {correct_answer}."
            feedback_class = "incorrect"

        session['fill_count'] += 1

        if session['fill_count'] >= 10:
            score = session['fill_score']
            total = session['fill_count']
            accuracy = int((score / total) * 100)

            session.pop('fill_score', None)
            session.pop('fill_count', None)
            session.pop('fill_correct_answer', None)

            return render_template(
                'fill_it_in_game_over.html',
                score=score,
                total=total,
                accuracy=accuracy
            )

    a = random.randint(1, 20)
    b = random.randint(1, 20)
    missing_position = random.choice(['first', 'second'])

    if missing_position == 'first':
        answer = a
        total_value = a + b
        question = f"___ + {b} = {total_value}"
    else:
        answer = b
        total_value = a + b
        question = f"{a} + ___ = {total_value}"

    session['fill_correct_answer'] = answer

    return render_template(
        'fill_it_in.html',
        question=question,
        score=session['fill_score'],
        count=session['fill_count'],
        feedback=feedback,
        feedback_class=feedback_class
    )

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)