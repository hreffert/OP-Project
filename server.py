from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import time
from datetime import datetime
import re
import todaysMatchs
import results
import concurrent.futures

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/fl"
mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route('/')
def index():
  cur = db.ODDS.aggregate([
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
                                          "$$this.country",
                                        ]
                                      ]
                                    }
                                  }
                                },
                                'seasons':{'$reduce':{'input':'$races', 'initialValue':[],'in':{'$concatArrays':["$$value",["$$this.season"]]}}},
                                '_id': 0
                              }
                            }
                          ])
  countryDD = []
  seasonsDD = []
  for item in cur:
    [countryDD.append(x) for x in item['races'] if x not in countryDD]
    [seasonsDD.append(x) for x in item['seasons'] if x not in seasonsDD]
  return render_template('index.html', data={"country":countryDD, "seasons":seasonsDD})
  
@app.route('/filter', methods = ['GET'])
def filter():
  country = request.args.get('country').split(',')
  league = request.args.get('league').split(',')
  dataFrame = request.args.get('df').split(',')
  seasons = request.args.get('season').split(',')
  
  country = [re.compile(e.strip(), re.I) for e in country if e not in ['', ' ']]
  league = [x.strip() for x in league if x not in ['', ' ']]
  dataFrame = [x.strip() for x in dataFrame if x not in ['', ' ']]
  seasons = [x.strip() for x in seasons if x not in ['', ' ']]
  
  q = [
        {'$match':{'races':{'$elemMatch':{'$and':[]}}}},
        {'$unwind':'$races'},
        {'$match':{}},
        {'$project':{'races':1, '_id':0}},
        {'$group' : {'_id' : "$_id", 'races' : { '$addToSet' : "$races" } }}
      ]
  if country == [] and league == [] and dataFrame == [] and seasons == []:
    #q = {}
    pass
  else:
    if country != []:
      q[0]['$match']['races']['$elemMatch']['$and'].append({'country':{'$in':country}})
    if league != []:
      q[0]['$match']['races']['$elemMatch']['$and'].append({'game':{'$in':league}})
    if seasons != []:
      q[0]['$match']['races']['$elemMatch']['$and'].append({'season':{'$in':seasons}})
      
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
        q[0]['$match']['races']['$elemMatch']['$and'].append({'Time':obj})  
  
  matchAnd = {}
  for item in q[0]['$match']['races']['$elemMatch']['$and']:
    matchAnd[f'races.{list(item.keys())[0]}'] = list(item.values())[0]
  
  q[2]['$match'] = matchAnd

  if len(q[0]['$match']['races']['$elemMatch']['$and']) == 0:
    q = [{'$project':{'_id':0}}]
    
  print("QUERY:", q)
  a = db.TEST.aggregate(q)
  data = [x for x in a]
  return {"status":200, "data":data}
  
@app.route('/launchScrap', methods = ['GET'])
def startScrap():
  script = request.args.get('script')
  EXECUTOR = concurrent.futures.ThreadPoolExecutor()
  if 'tResults' == script:
    EXECUTOR.submit(todaysMatchs.start)
  elif 'results' == script:
    EXECUTOR.submit(results.start)
  return {"status":200, "data":"SCRAPING HAS STARTED"}
  
if __name__ == '__main__':
  app.run(app, debug=True)

