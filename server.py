from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import time
from datetime import datetime
import re

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/fl"
mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route('/')
def index():
  cur = db.TEST.aggregate([
                            {
                              '$project': {
                                'races': {
                                  '$reduce': {
                                    'input': "$races",
                                    'initialValue': [],
                                    'in': {
                                      '$concatArrays': [
                                        "$$value",
                                        [
                                          "$$this.country"
                                        ]
                                      ]
                                    }
                                  }
                                },
                                '_id': 0
                              }
                            }
                          ])
  countryDD = []
  for item in cur:
    [countryDD.append(x) for x in item['races'] if x not in countryDD]
  return render_template('index.html', data=countryDD)
  
@app.route('/filter', methods = ['GET'])
def filter():
  country = request.args.get('country').split(',')
  league = request.args.get('league').split(',')
  country = [re.compile(e.strip(), re.I) for e in country if e not in ['', ' ']]
  league = [x.strip() for x in league if x not in ['', ' ']]
  
  q = {'races':
              {'$elemMatch':
                            {'$and':
                                  [{'country':
                                              {'$in':country}
                                   }, 
                                   {'game':
                                          {'$in':league}
                                   }
                                  ]
                            }
              }
      }
  a = db.TEST.find(q, {'_id':0})
  data = [x for x in a]
  return {"status":200, "data":data}
  
if __name__ == '__main__':
  app.run(app, debug=True)

