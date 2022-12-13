#https://realpython.com/primer-on-jinja-templating/#install-flask
#https://hackersandslackers.com/flask-jinja-templates/
#https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
# import requests as request
from flask import Flask, render_template, request, json, session
from flask_session import Session
import portfolio_optimization_lstm_prediction as polp
import stock_symbols as symbols
import keras
import os

# IMAGES = os.path.join('static', 'img')

static = os.path.abspath('static')

app = Flask(__name__, static_folder=static)

app.secret_key = "a very very very secret key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")


######## Sentiment analysis part#######################
import requests
from requests_oauthlib import OAuth1

import pandas as pd
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
################################################ TWITTER ######################################################
def create_url_twitter(keyword):
    consumer_key = '2GEDtzlFMJK6agAMkPQoVTwnl'
    consumer_secret = '9TvdpLsvdZDbUrihxDd2LUh02P3moWewdAWqTeupJH90SxPkoi'
    access_token = '1241443545975791617-Qy2ioSjn5qmKfHN17bSKV1RhWv19et'
    access_secret = 'asmAhYweQTDavRPwrs3FkdJd3557g76rcyksDNGT3b9Nx'

    auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
    
    url = 'https://api.twitter.com/1.1/search/tweets.json'

    query_params = {'q': keyword,
                    'count' : 100, 
                    'lang' : "en"   
                    }

    res = requests.get(url, params=query_params, auth=auth)
    return (res.json())

def twitter_api(company_list):
  df = pd.DataFrame(columns = ['post', 'keyword', 'date', 'link', "sentiment_score"])

  # to make sure that the tweets we see are connected with APPL as a stock 
  changed_company_list = []
  for i in range(len(company_list)):
    changed_company_list.append(company_list[i] + " AND " + "stock")

  # compund sentiment_score per stock
  compund_sentiment_per_stock = []


  for i in changed_company_list:
    tweets = create_url_twitter(i)
    for tweet in tweets['statuses']:
      if len(tweet["entities"]["user_mentions"])!=0:
        if tweet["text"] in df["post"].values:
          continue
        else:
          stock = i.split(" ")[0]
          sentiment_dict = SentimentIntensityAnalyzer().polarity_scores(tweet["text"])
          url = "https://twitter.com/i/web/status/" + tweet["id_str"]
          row = [tweet["text"], stock, tweet["created_at"], url, sentiment_dict["compound"]]
          df.loc[len(df.index)] = row

    stock_df = df.loc[df['keyword'] == stock]
    compund_sentiment_per_stock.append(round(stock_df["sentiment_score"].mean(), 3))

  return [df, compund_sentiment_per_stock]
################################################ TWITTER ######################################################
################################################ NEWS ######################################################
def news_create_url(keyword):
 
    API = '668b3afed7964ff4bba962c15faa74ec'
    url = 'https://newsapi.org/v2/everything?'
    parameter = {'q' : keyword,# topic 
              'apiKey': API,
              'sortBy':'popularity'
              }

    news_api = requests.get(url,params=parameter)

    return (news_api.json())

def news_api(company_list):
  df = pd.DataFrame(columns = ['title', 'keyword', 'date', 'link', "sentiment_score"])

  # to make sure that the tweets we see are connected with APPL as a stock 
  changed_company_list = []
  for i in range(len(company_list)):
    changed_company_list.append(company_list[i] + " AND " + "stock")

  # compund sentiment_score per stock
  compund_sentiment_per_stock = []

  for i in changed_company_list:
    newses = news_create_url(i)
    for news in newses['articles']:
      stock = i.split(" ")[0]
      sid_obj = SentimentIntensityAnalyzer()
      sentiment_dict = sid_obj.polarity_scores(news['content'])
      score = sentiment_dict['compound']
      title = news['title']
      url = news['url']
      date = news['publishedAt']
      row = [title, stock, date, url, sentiment_dict["compound"]]
      df.loc[len(df.index)] = row

    stock_df = df.loc[df['keyword'] == stock]
    compund_sentiment_per_stock.append(round(stock_df["sentiment_score"].mean(), 3))
  
  return [df, compund_sentiment_per_stock]


################################################ NEWS ######################################################

################################################ REDDIT ######################################################
import praw
import spacy

client_id = 'Qxc7nMBoS_35Rg4hpo4aLQ'
secret = 'j7ZhGG8zMkouebcIdAEYEkTNul85vw'
name = 'positech'
username = 'positech-22'
password = 'PROJECTSinprogramming22'

reddit = praw.Reddit(client_id = client_id,
                     client_secret = secret,
                     user_agent = name,
                     username = username,
                     password = password)

reddit.read_only = True

subreddit = reddit.subreddit('stocks+WallStreetBets+Investing')

posts = subreddit.new(limit=1000)

def reddit_api(company_list):
    df = pd.DataFrame(columns = ['post', 'keyword', 'date', 'link', "sentiment_score"])
    posts = subreddit.search(company_list)

    compound_sentiment_per_stock = []

    for post in posts:
        for word in company_list:
            if word in post.selftext:
                sentiment_dict = SentimentIntensityAnalyzer().polarity_scores(post.selftext)
                row = [post.selftext, word, post.created_utc, post.url, sentiment_dict["compound"]]
                df.loc[len(df.index)] = row

    for company in company_list:
        stock_df = df.loc[df['keyword']==company]
        compound_sentiment_per_stock.append(round(stock_df["sentiment_score"].mean(), 3))

    return [df, compound_sentiment_per_stock]

################################################ REDDIT ######################################################
@app.route("/sentiment_analysis", methods = ["GET", "POST"])
def sentiment_analysis():
    if (session['stock-list']):
        # stocks = request.form['stocks_list']
        # stocks = stocks.split(",") 
        stocks = session['stock-list']
        print("session data", stocks)
        

        reddit_data_and_scores = reddit_api(stocks)
        reddit_data = reddit_data_and_scores[0]
        reddit_data.to_csv("data/reddit_data.csv", index = False)
        reddit_sentiment_scores = reddit_data_and_scores[1]
        reddit_sentiment_scores.insert(0, "Reddit sentiment score ")

        twitter_data_and_scores = twitter_api(stocks)
        twitter_data = twitter_data_and_scores[0]
        twitter_data.to_csv("data/twitter_data.csv", index = False)
        twitter_sentiment_scores = twitter_data_and_scores[1]
        twitter_sentiment_scores.insert(0, "Twitter sentiment score ")

        news_data_and_scores = news_api(stocks)
        news_data = news_data_and_scores[0]
        news_data.to_csv("data/news_data.csv", index = False)
        news_sentiment_scores = news_data_and_scores[1]
        news_sentiment_scores.insert(0, "News sentiment score ")

    # else:
    #   stocks = ["Company 1", "Company 2", "Company 3"]
    #   reddit_sentiment_scores = ["Reddit sentiment score", "Nan","Nan", "Nan"]
    #   news_sentiment_scores = ["News sentiment score","Nan","Nan", "Nan"]
    #   twitter_sentiment_scores = ["Twitter sentiment score","Nan","Nan", "Nan"]
    #   news_data = pd.DataFrame()


    return render_template("sentiment_analysis.html", stocks = stocks, news_data = news_data, twitter_sentiment_scores = twitter_sentiment_scores, reddit_sentiment_scores = reddit_sentiment_scores, news_sentiment_scores = news_sentiment_scores )

@app.route("/twitter_data", methods = ["GET", "POST"])
def twitter_data():
    twitter_data = pd.read_csv("data/twitter_data.csv")
    return render_template("twitter_data.html", tables=[twitter_data.to_html(classes='data', index = False)], titles=twitter_data.columns.values)

@app.route("/news_data", methods = ["GET", "POST"])
def news_data():
    news_data = pd.read_csv("data/news_data.csv")
    return render_template("news_data.html", tables=[news_data.to_html(classes='data', index = False)], titles=news_data.columns.values)

@app.route("/reddit_data", methods = ["GET", "POST"])
def reddit_data():
    reddit_data = pd.read_csv("data/reddit_data.csv")
    reddit_data = reddit_data.iloc[:, 1:]
    return render_template("reddit_data.html", tables=[reddit_data.to_html(classes='data', index = False)], titles=reddit_data.columns.values)

#######################################

@app.route("/predictions")
def predictions():
    stocks = session['stock-list']
    images = []
    for s in stocks:
        file_path = f'/static/{s}_viz.png'
        # file_path = os.path.join(static, f'{s}_viz.png')
        images.append(file_path)
    # result = polp.LSTM_for_list_stock(stocks)
    # visualizations = polp.visualize_LSTM(result)
    # print(images)
    
    return render_template('predictions.html', images = images)
    # return render_template("predictions.html")

@app.route('/portfolio', methods=["GET", "POST"])
def visualize_lstm():
    session['client-portfolio'] = request.form
    stocks_str = request.form["stock-list"]
    stocks_raw = stocks_str.split(',')
    stocks_raw.pop()
    stocks = []
    for s in stocks_raw:
        stocks.append(s.strip())

    session['stock-list'] = stocks
    # images = []
    hist_data = request.form["hist-data"]
    print(hist_data)
    short_sale_str = request.form["short-sale"]
    if (short_sale_str=="True"):
        short_sale = True
    elif (short_sale_str=="False"):
        short_sale = False
    # short_sale = bool(short_sale_str)
    print(type(short_sale))

    # print(request.form["ind-weight"])
    ind_weight_str = request.form["ind-weight"]
    if (ind_weight_str == "None"):
        ind_weight = None
    else:
        ind_weight = float(ind_weight_str)
    print(ind_weight_str)
    amount = int(request.form["amount"])
    print(amount)

    portfolio_data = {"symbol_list": stocks, "interval" :"1mo", "year_ago": hist_data, "short_sale_constrain": short_sale, "ind_weight_constrain" : ind_weight, "invested_cash": amount}
    session["portfolio-data"] = portfolio_data
    client = polp.portfolio(symbol_list = stocks, interval="1mo", year_ago = hist_data, short_sale_constrain = short_sale, ind_weight_constrain = ind_weight, invested_cash = amount)
    # session["client"]=client
    stats, df = client.max_SR()
    client.show_price_plot();

    print(stats)
    print(df)

    img_path = os.path.join(static, 'price_plot.png')
    

    return render_template('portfolio.html', stats=stats, df=df)
    # for s in stocks:
    #     file_path = f'/static/{s}_viz.png'
    #     # file_path = os.path.join(static, f'{s}_viz.png')
    #     images.append(file_path)
    # # result = polp.LSTM_for_list_stock(stocks)
    # # visualizations = polp.visualize_LSTM(result)
    # # print(images)
    # session['stock-list'] = stocks
    # return render_template('lstm_prediction.html', images = images)
    


@app.route("/optimize-portfolio", methods=["GET", "POST"])
def optimize_portfolio():
    p_data = session["portfolio-data"]
    client = polp.portfolio(symbol_list = p_data["symbol_list"], interval=p_data["interval"], year_ago = p_data["year_ago"], short_sale_constrain = p_data["short_sale_constrain"], ind_weight_constrain = p_data["ind_weight_constrain"], invested_cash = p_data["invested_cash"])
    view = request.form.to_dict()
    bl_stat, df = client.Black_Litterman_model(view)
    client.back_test()

    return render_template("optimized-portfolio.html", stats = bl_stat, df=df)
    # return request.form
    # stocks_str = request.form["stock-list"]
    # stocks_raw = stocks_str.split(',')
    # stocks_raw.pop()
    # stocks = []
    # for s in stocks_raw:
    #     stocks.append(s.strip())
    
    # user_input_stock = "GOOGL"

    # if user_input_stock=="GOOGL":
    #     model = keras.models.load_model("googl_model")

    # pred_y = model.predict(test_x)
    # y_pred_price = target_normalizer.inverse_transform(pred_y)
    # # result
    # result_df = pd.DataFrame(data={"original":stock_df["Close"][len(stock_df)-len(y_pred_price):],"pred":list(y_pred_price .reshape(1,len(y_pred_price ))[0])})
    # result_dic[i] = result_df


    # # print(stocks)

    # hist_data = request.form["hist-data"]
    # print(hist_data)
    # short_sale_str = request.form["short-sale"]
    # if (short_sale_str=="True"):
    #     short_sale = True
    # elif (short_sale_str=="False"):
    #     short_sale = False
    # short_sale = bool(short_sale_str)
    # print(type(short_sale))

    # print(request.form["ind-weight"])
    # ind_weight_str = request.form["ind-weight"]
    # if (ind_weight_str == "None"):
    #     ind_weight = None
    # else:
    #     ind_weight = float(ind_weight_str)
    # print(ind_weight_str)
    # amount = int(request.form["amount"])
    # print(amount)
    # client = polp.portfolio(symbol_list = session['stock-list'], interval="1mo", year_ago = hist_data, short_sale_constrain = short_sale, ind_weight_constrain = ind_weight, invested_cash = amount)
    # session["client"] = client

    # stats, df = client.max_SR()
    # print(stats)
    # print(df)

    # return render_template('portfolio.html', stats=stats, df=df)

# @app.route('/constraints', methods=['POST', 'GET'])
# def add_constraints():
#     return render_template('constraints.html', stocks= session["stock-list"])

@app.route("/stocks", methods=['GET','POST'])
def portfolio():
    # if request.method == 'GET':
    # symbol_list = json.dumps(symbols.getStockSymbolList())
    # print(symbol_list)
    symbol_list = json.dumps(['AAPL', 'GOOGL', 'IBM', 'JPM', 'META'])
    return render_template("stocks.html", symbols=symbol_list)

    # if request.method == 'POST':
    #     return 'hey'
    # return render_template("portfolio.html")

if __name__=="__main__":
    app.run(debug=True)