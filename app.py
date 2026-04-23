import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for

from model1 import run_mlp, predict_seat
from model2 import run_sentiment, calculate_sentiment_score
from sentiment import classify_tweet

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- CREATE FOLDERS ----------------
for folder in ["data", "static", "uploads"]:
    os.makedirs(folder, exist_ok=True)


# ================= HOME =================
@app.route('/')
def home():
    session.clear()
    return render_template('home.html')


# ================= MODEL 1 =================
@app.route('/model1', methods=['GET', 'POST'])
def model1():

    if request.method == 'POST':

        # -------- PREDICT BUTTON --------
        if 'predict_btn' in request.form:
            vote = request.form.get("vote_input")

            if vote:
                prediction = predict_seat(float(vote))
                session['prediction1'] = prediction

        # -------- DATASET BUTTON --------
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
                    return render_template("model1.html", error="⚠️ No file selected!")

            result, graph = run_mlp(path)

            session['result1'] = result
            session['graph1'] = graph

            return redirect(url_for('model1'))

    return render_template(
        'model1.html',
        prediction=session.get('prediction1'),
        result=session.get('result1'),
        graph=session.get('graph1')
    )


# ================= MODEL 2 =================
@app.route('/model2', methods=['GET', 'POST'])
def model2():

    if 'pos' not in session:
        session['pos'] = 0
        session['neg'] = 0
        session['neu'] = 0

    error = None

    if request.method == 'POST':

        # -------- RESET --------
        if 'reset' in request.form:
            session.clear()
            return redirect(url_for('model2'))

        # -------- SAMPLE --------
        if 'sample' in request.form:
            path = "data/sample_model2.csv"

        # -------- UPLOAD --------
        else:
            file = request.files.get('file')

            if file and file.filename != "":
                filename = str(uuid.uuid4()) + "_" + file.filename
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
            else:
                return render_template("model2.html", error="⚠️ No file chosen!",
                    result=session.get('result2'),
                    graph=session.get('graph2'),
                    sentiment_result=session.get('sentiment_result'),
                    score=session.get('score'),
                    pos=session.get('pos',0),
                    neg=session.get('neg',0),
                    neu=session.get('neu',0)
                )

        # -------- RUN SENTIMENT MODEL --------
        result, graph = run_sentiment(path)

        session['result2'] = result
        session['graph2'] = graph

        # -------- TWEET ANALYSIS --------
        tweet = request.form.get("tweet")

        if tweet:
            sentiment = classify_tweet(tweet)
            session['sentiment_result'] = sentiment

            if sentiment == "Positive":
                session['pos'] += 1
            elif sentiment == "Negative":
                session['neg'] += 1
            else:
                session['neu'] += 1

            session['score'] = calculate_sentiment_score(
                session['pos'],
                session['neg'],
                session['neu']
            )

        return redirect(url_for('model2'))

    return render_template(
        "model2.html",
        error=error,
        result=session.get('result2'),
        graph=session.get('graph2'),
        sentiment_result=session.get('sentiment_result'),
        score=session.get('score'),
        pos=session.get('pos', 0),
        neg=session.get('neg', 0),
        neu=session.get('neu', 0)
    )


# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
