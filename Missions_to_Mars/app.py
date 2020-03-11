from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

conn = 'mongodb://localhost:27017'
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars"
mongo = PyMongo(app)

@app.route('/')
def index():
    mars = mongo.db.mars.find_one()
    return render_template('index.html', mars=mars)

@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_stuff = scrape_mars.scrape()
    mars.update({}, mars_stuff, upsert=True)
    return redirect("/", code=302)#information from scraping to other methods
    
if __name__ == "__main__":
    app.run(debug=True)