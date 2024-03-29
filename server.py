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
                                'league':{'$reduce':{'input':'$races', 'initialValue':[],'in':{'$concatArrays':["$$value",["$$this.league"]]}}},
                                '_id': 0,
                                'year':1,
                              }
                            }
                          ])
  countryDD = []
  leagueDD = []
  yearsDD = []
  for item in cur:
    if type(item.get('races')) == list:
      [countryDD.append(x) for x in item['races'] if x not in countryDD and x not in ['', ' ', None]]
    if type(item.get('league')) == list:
      [leagueDD.append(x) for x in item['league'] if x not in leagueDD and x not in ['', ' ', None]]
    y = item.get('year')
    if y not in [None, '', ' '] and y not in yearsDD:
      yearsDD.append(y)

  return render_template('index.html', data={"country":countryDD, "league":leagueDD, "seasons":sorted(yearsDD)})
  
@app.route('/filter', methods = ['GET'])
def filter():
  country = request.args.get('country').split(',')
  league = request.args.get('league').split(',')
  dataFrame = request.args.get('df').split(',')
  seasons = request.args.get('season').split(',')
  oddsCompare = request.args.get('oddsCompare')
  oddsTime = request.args.get('oddsTime')
  minOdds = request.args.get('minOdds')
  maxOdds = request.args.get('maxOdds')
  
  
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
      q[0]['$match']['races']['$elemMatch']['$and'].append({'league':{'$in':league}})
    if seasons != []:
      q[0]['$match']['year'] = {'$in':seasons}
      
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
    if 'year' not in q[0]['$match']:
      q = [{'$project':{'_id':0}}]
    else:
      q[0]['$match'].pop('races')
    
  print("QUERY:", q)
  a = db.ODDS.aggregate(q)
  data = [x for x in a]
  return {"status":200, "data":data}
  
@app.route('/launchScrap', methods = ['GET'])
def startScrap():
  script = request.args.get('script')
  EXECUTOR = concurrent.futures.ThreadPoolExecutor()
  if 'tResults' == script:
    EXECUTOR.submit(todaysMatchs.start, db)
  elif 'results' == script:
    EXECUTOR.submit(results.start, db)
  return {"status":200, "data":"SCRAPING HAS STARTED"}
  
if __name__ == '__main__':
  app.run(host='0.0.0.0',port='80', debug=True)

