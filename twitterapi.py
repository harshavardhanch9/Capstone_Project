from textblob import TextBlob
import tweepy
import configparser
import matplotlib.pyplot as plt


config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']


def tweets_polarity(ticker, no_of_tweets):

    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    tweets = tweepy.Cursor(api.search_tweets, tweet_mode='extended', q=ticker, lang= "en").items(no_of_tweets)

    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    tweet_list = []
    for tweet in tweets:
        text_list = tweet.full_text
        tweet_list.append(text_list)
        text = tweet.full_text.replace('RT','')
        if text.startswith(' @'):
            position = text.index(':')
            #print("pos:", position)
            text = text[position+2:]
        if text.startswith(' @'):
            position = text.index(' ')
            text = text[position+2:]
        analysis = TextBlob(text)
        tweet_polarity = analysis.sentiment.polarity

        #print(f' tweet polarity: {tweet_polarity}')
        if tweet_polarity > 0.00:
            positive += 1
        elif tweet_polarity < 0.00:
            negative += 1
        elif tweet_polarity == 0:
            neutral += 1

        polarity += tweet_polarity

        
    
    print(f'polarity: {polarity}', f'positive tweets: {positive}', f'negative tweets: {negative}', f'neutral tweets: {neutral}')
    labels = ['Positive', 'Negtive', 'Neutral']
    sizes = [positive, negative, neutral]
    plt.pie(sizes, labels= labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('static/sentiment.png')
    plt.close()
    #plt.show()

    if polarity > 0:
        tweet_pol = "Positive 😊😊😊"
        print(f'Sentiment of {ticker} is {tweet_pol}')
    else:
        tweet_pol = "Negative 😞😞😞"
        print(f'Sentiment of {ticker} is {tweet_pol}')
        #Neutral😐😐😐
    return tweet_list, polarity, tweet_pol, positive, negative, neutral 
