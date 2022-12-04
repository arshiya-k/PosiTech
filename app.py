#https://realpython.com/primer-on-jinja-templating/#install-flask
#https://hackersandslackers.com/flask-jinja-templates/
# import requests as request
from flask import Flask, render_template, request, json
import portfolio_optimization_lstm_prediction as polp
import stock_symbols as symbols

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/portfolio-optimization", methods=['GET','POST'])
def portfolio():
    if request.method == 'GET':
        symbol_list = json.dumps(symbols.getStockSymbolList())
        return render_template("portfolio.html", symbols=symbol_list)

    if request.method == 'POST':
        return render_template('about.html')
    # return render_template("portfolio.html")

if __name__=="__main__":
    app.run(debug=True)