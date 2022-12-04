#https://realpython.com/primer-on-jinja-templating/#install-flask
#https://hackersandslackers.com/flask-jinja-templates/
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/portfolio-optimization")
def portfolio():
    return render_template("portfolio.html")

if __name__=="__main__":
    app.run(debug=True)