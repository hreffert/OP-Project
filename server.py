from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import time
from datetime import datetime
import re
import todaysMatchs
import results

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
  dataFrame = request.args.get('df').split(',')
  
  country = [re.compile(e.strip(), re.I) for e in country if e not in ['', ' ']]
  league = [x.strip() for x in league if x not in ['', ' ']]
  dataFrame = [x.strip() for x in dataFrame if x not in ['', ' ']]
  
  q = {'races':
              {'$elemMatch':
                            {'$and':
                                    [
                                    ]
                            }
              }
      }
  if country == [] and league == [] and dataFrame == []:
    #q = {}
    pass
  else:
    if country != []:
      q['races']['$elemMatch']['$and'].append({'country':{'$in':country}})
    if league != []:
      q['races']['$elemMatch']['$and'].append({'game':{'$in':league}})
      
    if dataFrame != []:
      obj = {}
      if 'TMatches' in dataFrame:
        sDate = round(datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d').timestamp())
        eDate = sDate + 86400 
        obj['$gte'] = sDate 
        obj['$lte'] = eDate
        
      if 'Database' in dataFrame:
        sDate = round(datetime.now().timestamp())
        obj['$lte'] = sDate
        
      if 'UpEvents' in dataFrame:
        sDate = round(datetime.now().timestamp())
        obj['$gte'] = sDate
        
      if 'UpEvents' in dataFrame and 'Database' in dataFrame:
        pass
      else:
        q['races']['$elemMatch']['$and'].append({'Time':obj})  
    
    
  if len(q['races']['$elemMatch']['$and']) == 0:
    q = {}
    
    #print(22, q)
  a = db.TEST.find(q, {'_id':0})
  data = [x for x in a]
  return {"status":200, "data":data}
  
@app.route('/launchScrap', methods = ['GET'])
def startScrap():
  script = request.args.get('script')
  print(script)
  if 'tResults' == script:
    todaysMatchs.start()
  elif 'results' == script:
    results.start()
  return {"status":200, "data":"SCRAPING HAS STARTED"}
  
if __name__ == '__main__':
  app.run(app, debug=True)

