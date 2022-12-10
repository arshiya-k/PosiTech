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

IMAGES = os.path.join('static', 'img')

app = Flask(__name__, static_folder='/static')

app.secret_key = "secret key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/visualize-lstm', methods=["GET", "POST"])
def visualize_lstm():
    stocks_str = request.form["stock-list"]
    stocks_raw = stocks_str.split(',')
    stocks_raw.pop()
    stocks = []
    for s in stocks_raw:
        stocks.append(s.strip())

    images = []

    for s in stocks:
        file_path = os.path.join(IMAGES, f'{s}_viz.png')
        images.append(file_path)
    # result = polp.LSTM_for_list_stock(stocks)
    # visualizations = polp.visualize_LSTM(result)

    return render_template('lstm_prediction.html', images = images)
    


@app.route("/optimize-portfolio", methods=["GET", "POST"])
def optimize_portfolio():
    stocks_str = request.form["stock-list"]
    stocks_raw = stocks_str.split(',')
    stocks_raw.pop()
    stocks = []
    for s in stocks_raw:
        stocks.append(s.strip())
    
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

    # short_sale_str = request.form["short-sale"]
    # short_sale = bool(short_sale_str)

    # ind_weight_str = request.form["ind-weight"]
    # if (ind_weight_str == "None"):
    #     ind_weight = None
    # else:
    #     ind_weight = int(ind_weight_str)
    
    # amount = int(request.form["amount"])

    print(stocks, "1mo", hist_data, short_sale, ind_weight)
    client = polp.portfolio(stocks, hist_data, short_sale_str, ind_weight, amount)
    # session["client"] = client

    return (stocks)

@app.route("/stocks", methods=['GET','POST'])
def portfolio():
    # if request.method == 'GET':
    # symbol_list = json.dumps(symbols.getStockSymbolList())
    symbol_list = ['AAPL', 'GOOGL', 'IBM', 'JPM', 'META']
    return render_template("stocks.html", symbols=symbol_list)

    # if request.method == 'POST':
    #     return 'hey'
    # return render_template("portfolio.html")

if __name__=="__main__":
    app.run(debug=True)