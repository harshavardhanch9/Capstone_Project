from distutils.log import debug
from http.client import NOT_FOUND
from operator import index
from flask import Flask, request, render_template, redirect, url_for
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from wtform import RegistrationForm
from wtform import * 
from db import *
from twitterapi import *
#from passlib.hash import pbkdf2_sha256
import matplotlib.pyplot as plt
from lstm_prediction import final_out
from lstm_prediction import recommend
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe('spacytextblob')

app = Flask(__name__)
app.secret_key = 'replace later'


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
#app.config["SQLALCHEMY_BINDS"] = {'nasdaq' : "sqlite:///nasdaq.db"}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db.init_app(app) ## initialize the database
db.create_all(app=app) ## create table

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        #hashed_password = pbkdf2_sha256.hash(password)

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('home.html', form=reg_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        return redirect(url_for('predict'))

    return render_template("login.html", form=login_form)


@app.route('/contact')
def Contact():
    return render_template('contact.html')


@app.route('/sentiment', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        try:
            searchword = request.form.get('typetext')
            no_tweets = int(request.form.get('typetweets'))
            tweet_list, polarity, tweet_pol, positive, negative, neutral = tweets_polarity(searchword, no_tweets)
            
            return render_template('sentiment.html', prediction=tweet_pol, searchword = searchword, tweet_list= tweet_list)
        except:
            return render_template('sentiment.html')

    return render_template('sentiment.html')


@app.route('/Predict', methods=['GET','POST'])
def predict():

    if request.method == 'POST':
        try:
            name = request.form.get('typeticker')
            days = int(request.form.get('typedays'))
            no_tweets = int(request.form.get('typetweets'))
            db = create_db(name)
            data = get_stock(name) 
            df = pd.DataFrame(data)
            today_data = df.iloc[-1:]
            finals, mean =final_out(df, days)
            tweet_list, polarity, tweet_pol, positive, negative, neutral = tweets_polarity(name, no_tweets)
            expect, movement = recommend(today_data, mean)

            present = today_data['Close'].item()
            if present < mean:
                if polarity >0:
                    idea = "RISE"
                    decision = "BUY"
                elif polarity <= 0:
                    idea = "FALL"
                    decision = "SELL"
            else:
                idea = "FALL"
                decision = "SELL"
   
            return render_template('stock_predict.html', stock = name, period = days, output = finals, expect = expect, movement= movement, open_price = today_data['Open'].to_string(index=False),
            close_price = today_data['Close'].to_string(index=False), high_price = today_data['High'].to_string(index=False),low_price = today_data['Low'].to_string(index=False), 
            volume = today_data['Volume'].to_string(index=False), prediction=tweet_pol, tweet_list= tweet_list, idea = idea, decision = decision)
        except:
            return render_template('stock_predict.html')

    # if request.method == 'POST':
    #     try:
    #         searchword = request.form.get('typetext')
    #         no_tweets = int(request.form.get('typetweets'))
    #         tweet_list, polarity, tweet_pol, positive, negative, neutral = tweets_polarity(searchword, no_tweets)
            
    #         return render_template('stock_predict.html', prediction=tweet_pol, searchword = searchword, tweet_list= tweet_list)
    #     except:
    #         return render_template('stock_predict.html')

    return render_template('stock_predict.html')

@app.route('/tools')
def Tools():
    return render_template('tools.html')


if __name__ == '__main__':
    app.run(debug=True)