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