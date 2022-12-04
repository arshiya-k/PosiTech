#https://realpython.com/primer-on-jinja-templating/#install-flask
#https://hackersandslackers.com/flask-jinja-templates/
#https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
# import requests as request
from flask import Flask, render_template, request, json, session
from flask_session import Session
import portfolio_optimization_lstm_prediction as polp
import stock_symbols as symbols


app = Flask(__name__)
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

@app.route("/optimize-portfolio", methods=["GET", "POST"])
def optimize_portfolio():
    stocks_str = request.form["stock-list"]
    stocks_raw = stocks_str.split(',')
    stocks_raw.pop()
    stocks = []
    for s in stocks_raw:
        stocks.append(s.strip())

    # print(stocks)

    hist_data = request.form["hist-data"]

    short_sale_str = request.form["short-sale"]
    short_sale = bool(short_sale_str)

    ind_weight_str = request.form["ind-weight"]
    if (ind_weight_str == "None"):
        ind_weight = None
    else:
        ind_weight = int(ind_weight_str)
    print(stocks, "1mo", hist_data, short_sale, ind_weight)
    client = polp.portfolio(stocks, "1mo", hist_data, short_sale, ind_weight)
    # session["client"] = client

    return (stocks)

@app.route("/portfolio", methods=['GET','POST'])
def portfolio():
    # if request.method == 'GET':
    symbol_list = json.dumps(symbols.getStockSymbolList())
    return render_template("portfolio.html", symbols=symbol_list)

    # if request.method == 'POST':
    #     return 'hey'
    # return render_template("portfolio.html")

if __name__=="__main__":
    app.run(debug=True)