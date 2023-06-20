from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import time
from datetime import datetime

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/fl"
mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route('/')
def index():
  return render_template('index.html')
  
@app.route('/filter', methods = ['GET'])
def filter():
  a = db.TEST.find({}, {'_id':0})
  data = [x for x in a]
  return {"status":200, "data":data}
  
if __name__ == '__main__':
  app.run(app, debug=True)

