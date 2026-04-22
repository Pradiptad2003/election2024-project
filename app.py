import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for

from model1 import run_mlp, predict_seat
from model2 import run_sentiment, calculate_sentiment_score
from sentiment import classify_tweet

app = Flask(__name__)

# 🔥 SECRET KEY
app.secret_key = "supersecretkey"

# 🔥 IMPORTANT: Render এর জন্য /tmp ব্যবহার করো
UPLOAD_FOLDER = "/tmp"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders exist
for folder in ["data", "static"]:
    if not os.path.exists(folder):
        os.makedirs(folder)


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('home.html')


# ---------------- MODEL 1 ----------------
@app.route('/model1', methods=['GET', 'POST'])
def model1():

    prediction = None

    if request.method == 'POST':

        # 🔵 PREDICT
        if 'predict_btn' in request.form:
            vote = request.form.get("vote_input")

            if vote:
                prediction = predict_seat(float(vote))

        # 🟢 DATASET
        elif 'dataset_btn' in request.form or 'sample' in request.form:

            if 'sample' in request.form:
                path = "data/sample_model1.csv"

            else:
                file = request.files.get('file')

                if file and file.filename != "":
                    # 🔥 UNIQUE filename
                    filename = str(uuid.uuid4()) + "_" + file.filename
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                else:
                    return "⚠️ No file uploaded!"

            result, graph = run_mlp(path)

            # 🔥 store in session (fix back error)
            session['result1'] = result
            session['graph1'] = graph

            return redirect(url_for('model1'))

    return render_template('model1.html',
                           prediction=prediction,
                           result=session.get('result1'),
                           graph=session.get('graph1'))


# ---------------- MODEL 2 ----------------
@app.route('/model2', methods=['GET', 'POST'])
def model2():

    if 'pos' not in session:
        session['pos'] = 0
        session['neg'] = 0
        session['neu'] = 0

    if request.method == 'POST':

        # 🔄 RESET FIRST
        if 'reset' in request.form:
            session['pos'] = 0
            session['neg'] = 0
            session['neu'] = 0
            return redirect(url_for('model2'))

        # -------- DATASET --------
        file = request.files.get('file')

        if 'sample' in request.form:
            path = "data/sample_model2.csv"

        elif file and file.filename != "":
            filename = str(uuid.uuid4()) + "_" + file.filename
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
        else:
            path = "data/sample_model2.csv"

        result, graph = run_sentiment(path)

        # -------- TWEET --------
        tweet = request.form.get("tweet")

        if tweet:
            sentiment_result = classify_tweet(tweet)

            if sentiment_result == "Positive":
                session['pos'] += 1
            elif sentiment_result == "Negative":
                session['neg'] += 1
            else:
                session['neu'] += 1

            score = calculate_sentiment_score(
                session['pos'],
                session['neg'],
                session['neu']
            )
        else:
            sentiment_result = None
            score = None

        # 🔥 store session
        session['result2'] = result
        session['graph2'] = graph
        session['sentiment_result'] = sentiment_result
        session['score'] = score

        return redirect(url_for('model2'))

    return render_template('model2.html',
                           result=session.get('result2'),
                           graph=session.get('graph2'),
                           sentiment_result=session.get('sentiment_result'),
                           score=session.get('score'),
                           pos=session['pos'],
                           neg=session['neg'],
                           neu=session['neu'])


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True) ata app er code
