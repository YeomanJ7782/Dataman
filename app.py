from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'secret123'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/answer_checker', methods=['GET', 'POST'])
def answer_checker():
    # initialize session values
    if 'score' not in session:
        session['score'] = 0
        session['count'] = 0

    # handle answer submission
    if request.method == 'POST':
        user_answer = request.form['answer'] == 'true'
        correct = session.get('correct', False)

        if user_answer == correct:
            session['score'] += 1

        session['count'] += 1

    # check if game is over
    if session['count'] >= 5:
        score = session['score']
        session.clear()
        return render_template('game_over.html', score=score)

    # generate new question
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    correct = a + b

    if random.choice([True, False]):
        shown = correct
    else:
        shown = correct + random.randint(-3, 3)

    session['correct'] = (shown == correct)

    return render_template(
        'answer_checker.html',
        question=f"{a} + {b} = {shown}",
        score=session['score'],
        count=session['count']
    )

if __name__ == '__main__':
    app.run(debug=True)