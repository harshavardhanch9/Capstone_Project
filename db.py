from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from lstm_prediction import get_nasdaq100_tickers
import pandas as pd
import yfinance as yf

db = SQLAlchemy()

class User(db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
        }

# def getdata(tickers):
#     data = []

#     for ticker in tickers:
#         data.append(yf.download(ticker, interval='1d', period='10y', rounding = True))

#     return data
# nasdaq_tickers = get_nasdaq100_tickers()
# Nasdaq = getdata(nasdaq_tickers)

# def create_db(Nasdaq, nasdaq_tickers):

#     try:
#         engine = create_engine("sqlite:///nasdaq.db")
#         #conn = engine.connect()
#         for stock, ticker in zip(Nasdaq, nasdaq_tickers):
#             stock.to_sql(ticker, engine, if_exists='replace')
#             #conn.close()
#         return 0

#     except:
#         return 1

# create_db(Nasdaq, nasdaq_tickers)

# def getdata(tickers):
#     data = []
#     for ticker in tickers:
#         data.append(yf.download(ticker, interval='1d', period='10y', rounding = True))

#     return data
# Nasdaq = getdata('AAPL')
# nasdaq_tickers= 'AAPL'

def create_db(ticker):
    stock = yf.download(ticker, interval='1d', period='10y', rounding = True)
    try:
        engine = create_engine("sqlite:///nasdaq.db")
    
        stock.to_sql(ticker, engine, if_exists='replace')
    
        return 0

    except:
        return 1


def get_stock(table):
    try:
        engine = create_engine("sqlite:///nasdaq.db")
        conn = engine.connect()

        dt = pd.read_sql_query("SELECT * FROM '{}'". format(table), conn)
        conn.close()

        return dt.to_dict()

    except:
        return {"ERROR": "NO Ticker WAS FOUND"}