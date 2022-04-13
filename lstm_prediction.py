#from sympy import symbols
from unicodedata import decimal
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup as bs
import datetime
import requests
import torch
from torch.autograd  import Variable
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import lstms

scaler = MinMaxScaler(feature_range=(0,1))

# scrapping nasdaq100 stock symbols from wikipedia
def get_nasdaq100_tickers():
    now = datetime.datetime.utcnow()
    response = requests.get('https://en.wikipedia.org/wiki/Nasdaq-100')

    soup = bs(response.text)
    symbol_list = soup.select('table')[3].select('tr')[1:]

    symbols = []

    for i, symbol in enumerate(symbol_list):
        tds = symbol.select('td')
        symbols.append(tds[1].text)
    return symbols

# Getting data from yahoo finance
def get_data(file='data.csv'):
    #symbols = get_nasdaq100_tickers()
    #df = yf.download(symbols, interval='1d', period='20y', rounding = True)

    #df.to_csv('data.csv')

    df1 = pd.read_csv(file, parse_dates= True, header=[0,1], index_col=0)

    idx = pd.IndexSlice
    df2 = df1.loc[:,idx['Close', 'AAPL']]   
    df2 = df2.dropna()

    training_size = int(len(df2)*0.7)
    test_size = len(df2)-training_size
    train_data, test_data = df2[0:training_size],df2[training_size:len(df2)]
    scaler = MinMaxScaler(feature_range=(0,1))
    train_data_scaled = scaler.fit_transform(np.array(train_data).reshape(-1,1))
    test_data_scaled = scaler.transform(np.array(test_data).reshape(-1,1))

    return train_data_scaled, test_data_scaled, scaler

# arraging data into timesteps
def timeseries_dataset(data, time_step):
    X_data, Y_data = [], []
    for i in range(len(data)-time_step-1):
        a = data[i:(i+time_step)]
        X_data.append(a)
        Y_data.append(data[i + time_step])
    return np.array(X_data), np.array(Y_data)

def final_out(df,days):
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df1 = df[['Close', 'Date']].set_index('Date')
    plt.plot(df1)    
    plt.legend(loc=4)
    plt.xlabel("Year")
    plt.ylabel("Price")
    plt.grid()
    plt.savefig('static/trend.png')
    plt.close()
    df = df['Close']
    #scaler = MinMaxScaler(feature_range=(0,1))
    test_data= df[int(len(df)*0.85):len(df)]
    test_data_scaled = scaler.fit_transform(np.array(test_data).reshape(-1,1))
    X_input=test_data_scaled[(len(test_data_scaled)-100):].reshape(1,-1)
    temp_input=list(X_input)
    temp_input=temp_input[0].tolist()

    input_size = 1
    hidden_size = 32
    num_layers = 2
    output_size = 1

    model = lstms.LSTM(input_size, hidden_size, num_layers, output_size )
    model.load_state_dict(torch.load('lstm_model100_32_0.01_2000.pth'))
    model.eval()


    lst_output=[]
    n_steps=100
    i=0
    #days=15
    while(i<days):
        
        if(len(temp_input)>100):
            #print(temp_input)
            x_input=np.array(temp_input[1:])
            #print("{} day input {}".format(i,x_input))
            x_input = x_input.reshape(1,-1)
            x_input = x_input.reshape((1, n_steps, 1))
            x_input = Variable(torch.Tensor(x_input))
            yhat = model(x_input)
            #print("{} day output {}".format(i,yhat))
            temp_input.extend(yhat[0].tolist())
            temp_input=temp_input[1:]
            #print(temp_input)
            lst_output.extend(yhat.tolist())
            i=i+1
        else:
            x_input = X_input.reshape((1, n_steps,1))
            x_input = Variable(torch.Tensor(x_input))
            yhat = model(x_input)
            #print(yhat[0])
            temp_input.extend(yhat[0].tolist())
            #print(len(temp_input))
            lst_output.extend(yhat.tolist())
            i=i+1
    

    time_step = 100
    x_data, y_data = timeseries_dataset(test_data_scaled, time_step)
    x_data = x_data.reshape(x_data.shape[0], x_data.shape[1], 1)
    y_data = y_data.reshape(y_data.shape[0],1)
    x_data = Variable(torch.Tensor(x_data))
    y_data = Variable(torch.Tensor(y_data))
    y_predict = model(x_data)
    y_predict = pd.DataFrame(scaler.inverse_transform(y_predict.detach().numpy()))
    y_original = pd.DataFrame(scaler.inverse_transform(y_data.detach().numpy()))

    plt.plot(y_original,label='Actual Price')  
    plt.plot(y_predict,label='Predicted Price')
        
    plt.legend(loc=4)
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.grid()
    plt.savefig('static/lstm.png')
    plt.close()
    
    today_data = df.iloc[-1:]
    predicted_price = scaler.inverse_transform(lst_output)
    mean = predicted_price.mean()

    predicted_price = np.round_(predicted_price, decimals=2)

    return predicted_price, mean

def recommend(today_data, mean):
    price = today_data['Close'].item()
    if price < mean:
        chance = "RISE"
        trade = "BUY"
    else:
        chance = "FALL"
        trade = "SELL"
    return chance, trade
