from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'secret123'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/answer_checker', methods=['GET', 'POST'])
def answer_checker():
    difficulty = request.args.get('difficulty') or session.get('difficulty', 'easy')
    session['difficulty'] = difficulty

    if 'score' not in session:
        session['score'] = 0
        session['count'] = 0
        session['streak'] = 0
        feedback = None
        feedback_class = None

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
        feedback=feedback,
        feedback_class=feedback_class
    )

if __name__ == '__main__':
    app.run(debug=True)