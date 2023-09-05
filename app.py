from flask import Flask, render_template, request, redirect, url_for, flash, session
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import time, datetime
from datetime import timedelta
from utils import sampleQuestion, get_db_connection, text_retriever, meme_retriever, submitQuestion, closeSurvey, get_unannotated_memes
from flask_ngrok import run_with_ngrok


# Flask==2.2.2
# flask-ngrok==0.0.25
# pandas==1.5.2
# firebase-admin==6.2.0
# gunicorn==20.0.4
# wfastcgi==3.0.0
# tzlocal==4.2

# To run
# nohup python3 app.py
# To stop
# lsof -t -i tcp:8000 | xargs kill -9

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Rckjr43jkiubfheriuggrb34f34'
# run_with_ngrok(app)


@app.route('/', methods = ['GET','POST'])
def loginPage():
    if("modelId" in session):
        print("Error")
        closeSurvey(session["modelId"], session["contextId"], session["memeId"], session["annotationId"])
    session.clear()

    userId = None
    password = None
    userId = None
    if("user_name" in session):
        user_name = session["user_name"]
    if("password" in session):
        password = session["password"]

    if request.method == 'GET':
        return render_template('loginPage.html')
    elif request.method == 'POST':
        if("user_name" in request.form):
            userId = request.form["user_name"]
            if(userId in [str(i) for i in range(1, 13)]):
                session["userId"] = userId
            else:
                userId = None
        else:
            userId = None
        if("password" in request.form):
            password = request.form["password"]
        else:
            password = None

        if(userId == None or password != "sutd_meme_project" ):
            print("Error")
            flash('Please enter the correct user name and password to continue the survey.')
            return redirect(url_for('loginPage'))
        else:
            return redirect(url_for('firstPage'))

@app.route('/firstPage', methods = ['GET','POST'])
def firstPage():
    hilarity_text = None
    support_text = None
    text = ""
    if("userId" in session and "modelId" not in session or "contextId" not in session or "memeId" not in session or "annotationId" not in session):
        modelId, contextId, memeId, annotationId, startTime= sampleQuestion(int(session["userId"]))
        unannotated_memes = get_unannotated_memes(int(session["userId"]))
        if(int(modelId) == -1):
            return redirect(url_for('notAvaiablePage'))
        
        text = text_retriever(modelId, contextId, memeId)
        session["modelId"] = str(modelId)
        session["contextId"] = str(contextId)
        session["memeId"] = str(memeId)
        session["annotationId"] = str(annotationId)
        session["startTime"] = str(startTime)
        session["text"] = str(text)
        session["unannotated_memes"] = unannotated_memes
        app.permanent_session_lifetime = timedelta(minutes=20, seconds=3) 
        session.modified = True
    modelId = int(session["modelId"] )

    if("hilarity_text" in session):
        hilarity_text = session["hilarity_text"]
    if("support_text" in session and modelId != 4):
        support_text = session["support_text"]
    if("text" in session):
        text = session["text"]

    if request.method == 'GET':
        return render_template('firstPage.html', text = text, modelId=modelId, hilarity_text = hilarity_text, support_text = support_text, unannotated_memes=session["unannotated_memes"], startTime=session["startTime"])
    elif request.method == 'POST':
        if("hilarity_text" in request.form):
            hilarity_text = request.form["hilarity_text"]
            session["hilarity_text"] = hilarity_text
        else:
            hilarity_text = None
        if("support_text" in request.form and modelId!=4):
            support_text = request.form["support_text"]
            session["support_text"] = support_text
        else:
            support_text = None
        if(hilarity_text == None or (support_text == None and modelId!=4)):
            flash('Answer all the questions before continuing the survey.')
            return redirect(url_for('firstPage'))
        else:
            return redirect(url_for('secondPage'))
    return redirect(url_for('notAvaiablePage'))

@app.route('/secondPage', methods = ['GET','POST'])
def secondPage():
    if("modelId" in session or "contextId" in session or "memeId" in session or "annotationId" in session and "hilarity_text" in session and "support_text" in session):
        modelId  = session["modelId"]
        contextId = session["contextId"]
        memeId = session["memeId"]
        annotationId = session["annotationId"]
        startTime = session["startTime"]
        if(int(modelId) < 0  or int(contextId) < 0 or int(memeId) < 0 or int(annotationId) < 0):
            session.clear()
            return redirect(url_for('notAvaiablePage'))

        meme_url = meme_retriever(int(modelId), int(contextId), int(memeId))
        print(meme_url)

        similar_meme = None
        hateful_meme = None
        hilarity_meme = None
        support_meme = None
        persuasiveness = None

        if("similar_meme" in session):
            similar_meme = session["similar_meme"]
        if("hateful_meme" in session):
            hateful_meme = session["hateful_meme"]
        if("hilarity_meme" in session):
            hilarity_meme = session["hilarity_meme"]
        if("support_meme" in session):
            support_meme = session["support_meme"]
        if("persuasiveness" in session):
            persuasiveness = session["persuasiveness"]

        if request.method == 'POST':
            if("similar_meme" in request.form):
                similar_meme = request.form["similar_meme"]
                session["similar_meme"] = similar_meme
            else:
                similar_meme = None
            if("hateful_meme" in request.form):
                hateful_meme = request.form["hateful_meme"]
                session["hateful_meme"] = hateful_meme
            else:
                hateful_meme = None
            if("hilarity_meme" in request.form):
                hilarity_meme = request.form["hilarity_meme"]
                session["hilarity_meme"] = hilarity_meme
            else:
                hilarity_meme = None
            if("support_meme" in request.form):
                support_meme = request.form["support_meme"]
                session["support_meme"] = support_meme
            else:
                support_meme = None
            if("persuasiveness" in request.form):
                persuasiveness = request.form["persuasiveness"]
                session["persuasiveness"] = persuasiveness
            else:
                persuasiveness = None

            if(int(modelId) == 4):
                if( similar_meme != None and hateful_meme != None and hilarity_meme != None ):
                    submitQuestion(session["userId"], modelId, contextId, memeId, annotationId, session["hilarity_text"], None, similar_meme,\
                    hateful_meme, hilarity_meme, None, None, startTime)
                    userId = session["userId"]
                    session.clear()
                    session["userId"] = userId
                    return redirect(url_for('firstPage'))
                else:
                    flash('Answer all the questions before submitting the survey.')
                    return redirect(url_for('secondPage'))
            else:
                if(similar_meme != None and hateful_meme != None and hilarity_meme != None and support_meme != None and persuasiveness != None ):
                    submitQuestion(session["userId"], modelId, contextId, memeId, annotationId, session["hilarity_text"], session["support_text"], similar_meme,\
                    hateful_meme, hilarity_meme, support_meme, persuasiveness, startTime)
                    userId = session["userId"]
                    session.clear()
                    session["userId"] = userId
                    return redirect(url_for('firstPage'))
                else:
                    flash('Answer all the questions before submitting the survey.')
                    return redirect(url_for('secondPage'))

        elif request.method == 'GET':
            return render_template('secondPage.html', modelId = modelId, meme_url=meme_url, similar_meme=similar_meme,hateful_meme=hateful_meme, \
                                    hilarity_meme=hilarity_meme,support_meme=support_meme,persuasiveness=persuasiveness, unannotated_memes=session["unannotated_memes"], startTime=session["startTime"])
        
    session.clear()
    return redirect(url_for('notAvaiablePage'))


@app.route('/notAvaiablePage')
def notAvaiablePage():
    return render_template('notAvaiablePage.html')

@app.route('/timeOutPage')
def timeOutPage():
    if("modelId" in session or "contextId" in session or "memeId" in session or "annotationId" in session):
        modelId  = session["modelId"]
        contextId = session["contextId"]
        memeId =  session["memeId"]
        annotationId = session["annotationId"]
        session.clear()
        closeSurvey(modelId, contextId, memeId, annotationId)
    return render_template('timeOutPage.html')

def checkTimeOut():
    cur_time = int(time.time())
    conn = get_db_connection()
    inProgress = conn.execute('SELECT * FROM inProgress').fetchall()
    for record in inProgress:
        startTime = record["startTime"]
        if((cur_time-startTime)//60 >= 30):
            modelId = record["modelId"]
            contextId = record["contextId"]
            memeId = record["memeId"]
            annotationId = record["annotationId"]
            closeSurvey(modelId, contextId, memeId, annotationId)

    conn.close()
    
with app.app_context():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=checkTimeOut, trigger="interval", seconds=30) # check
    scheduler.start()

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8000, debug=True)
    app.run()
