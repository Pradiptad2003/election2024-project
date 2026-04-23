import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for

from model1 import run_mlp, predict_seat
from model2 import run_sentiment, calculate_sentiment_score
from sentiment import classify_tweet

app = Flask(__name__)

app.secret_key = "supersecretkey"

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
STATIC_FOLDER = os.path.join(os.getcwd(), "static")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

for folder in ["data", "static", "uploads"]:
    if not os.path.exists(folder):
        os.makedirs(folder)


# ---------------- HOME ----------------
@app.route('/')
def home():
    session.clear()
    return render_template('home.html')


# ---------------- MODEL 1 ----------------
@app.route('/model1', methods=['GET', 'POST'])
def model1():

    prediction = None

    if request.method == 'POST':

        if 'predict_btn' in request.form:
            vote = request.form.get("vote_input")

            if vote:
                prediction = predict_seat(float(vote))
                session['prediction1'] = prediction

        elif 'dataset_btn' in request.form or 'sample' in request.form:

            if 'sample' in request.form:
                path = "data/sample_model1.csv"
            else:
                file = request.files.get('file')

                if file and file.filename != "":
                    filename = str(uuid.uuid4()) + "_" + file.filename
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                else:
                    return render_template('model1.html', error="⚠️ No file uploaded!")

            try:
                result, graph = run_mlp(path)
            except Exception as e:
                return f"Model1 Error: {str(e)}"

            session['result1'] = result
            session['graph1'] = graph

            return redirect(url_for('model1'))

    return render_template(
        'model1.html',
        prediction=session.get('prediction1'),
        result=session.get('result1'),
        graph=session.get('graph1')
    )


# ---------------- MODEL 2 ----------------
@app.route('/model2', methods=['GET', 'POST'])
def model2():

    if 'pos' not in session:
        session['pos'] = 0
        session['neg'] = 0
        session['neu'] = 0

    error = None

    if request.method == 'POST':

        if 'reset' in request.form:
            session.clear()
            return redirect(url_for('model2'))

        file = request.files.get('file')

        # -------- SAMPLE DATASET --------
        if 'sample' in request.form:
            path = "data/sample_model2.csv"

        # -------- FILE UPLOAD --------
        elif file and file.filename != "":
            filename = str(uuid.uuid4()) + "_" + file.filename
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

        # -------- NO FILE SELECTED --------
        else:
            return render_template(
                'model2.html',
                error="⚠️ No file chosen!",
                result=session.get('result2'),
                graph=session.get('graph2'),
                sentiment_result=session.get('sentiment_result'),
                score=session.get('score'),
                pos=session.get('pos', 0),
                neg=session.get('neg', 0),
                neu=session.get('neu', 0)
            )

        # -------- SENTIMENT MODEL SAFE RUN --------
        try:
            result, graph = run_sentiment(path)
        except Exception as e:
            return f"Model2 Error: {str(e)}"

        session['result2'] = result
        session['graph2'] = graph

        tweet = request.form.get("tweet")

        sentiment_result = None
        score = None

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

        session['sentiment_result'] = sentiment_result
        session['score'] = score

        return redirect(url_for('model2'))

    return render_template(
        'model2.html',
        error=error,
        result=session.get('result2'),
        graph=session.get('graph2'),
        sentiment_result=session.get('sentiment_result'),
        score=session.get('score'),
        pos=session.get('pos', 0),
        neg=session.get('neg', 0),
        neu=session.get('neu', 0)
    )


# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
